# @author Codex (gpt-5.6-sol)
"""将 SVN 修订历史安全地构造成新的本地 Git 历史。"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Sequence


DEFAULT_EXCLUDED_ROOTS = ("site", "sitemap", "topic", "downloads")


@dataclass(frozen=True)
class SvnChange:
    action: str
    kind: str
    relative_path: str


@dataclass(frozen=True)
class SvnRevision:
    number: int
    author: str
    date: str
    message: str
    changes: tuple[SvnChange, ...]


# 解析可带 r 前缀的 SVN 修订号。
# @param value - 命令行传入的 SVN 修订号。
# @returns 非负整数修订号。
def parse_revision_number(value: str) -> int:
    normalized = value[1:] if value.startswith(("r", "R")) else value
    if not normalized.isdigit():
        raise argparse.ArgumentTypeError(f"无效的 SVN 修订号: {value}")
    revision = int(normalized)
    if revision < 0:
        raise argparse.ArgumentTypeError("SVN 修订号不能小于 0")
    return revision


# 解析并校验命令行参数。
# @param argv - 不含程序名的命令行参数；为 None 时读取 sys.argv。
# @returns 校验后的参数命名空间。
def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="将 SVN 修订历史同步到本地 Git 引用")
    parser.add_argument("--base-ref", required=True, help="同步历史的 Git 基线引用")
    parser.add_argument("--new-branch", help="待创建的新本地同步分支")
    parser.add_argument(
        "--merge-target",
        nargs="?",
        const="master",
        help="将候选历史快进到既有本地分支；省略值时使用 master",
    )
    parser.add_argument("--svn-url", required=True, help="待同步的 SVN 目录 URL")
    parser.add_argument(
        "--revision",
        nargs="+",
        type=parse_revision_number,
        metavar="REV",
        help="一个起始修订号（结束取 SVN HEAD），或起止两个修订号（闭区间）",
    )
    parser.add_argument("--start", type=int, help="兼容参数：起始 SVN 修订号（含）")
    parser.add_argument("--end", type=int, help="兼容参数：结束 SVN 修订号（含）")
    parser.add_argument(
        "--exclude-root",
        action="append",
        default=[],
        metavar="NAME",
        help="排除 SVN URL 下的顶层目录，可重复指定",
    )
    parser.add_argument(
        "--no-default-excludes",
        action="store_true",
        help="清空 site、sitemap、topic、downloads 四个默认排除目录",
    )
    args = parser.parse_args(argv)
    if not args.new_branch and not args.merge_target:
        parser.error("必须指定 --new-branch 或 --merge-target")
    if args.new_branch and args.merge_target == args.new_branch:
        parser.error("--new-branch 与 --merge-target 不能同名")
    has_legacy_range = args.start is not None or args.end is not None
    if args.revision and has_legacy_range:
        parser.error("--revision 不能与 --start/--end 混用")
    if args.revision:
        if len(args.revision) > 2:
            parser.error("--revision 只能填写一个或两个 SVN 修订号")
        if len(args.revision) == 2 and args.revision[0] > args.revision[1]:
            parser.error("修订范围反序：第一个修订号必须小于或等于第二个修订号")
    elif has_legacy_range:
        if args.start is None or args.end is None:
            parser.error("--start 与 --end 必须成对出现")
        if args.start < 0 or args.end < args.start:
            parser.error("修订范围必须满足 0 <= start <= end")
    else:
        parser.error("必须指定 --revision，或成对指定 --start 与 --end")
    for value in args.exclude_root:
        if not value or "/" in value or value in {".", ".."}:
            parser.error("--exclude-root 必须是单个非空顶层目录名")
    if not args.no_default_excludes:
        args.exclude_root = [*DEFAULT_EXCLUDED_ROOTS, *args.exclude_root]
    return args


# 执行外部命令并在失败时携带命令输出终止。
# @param command - 命令及参数列表。
# @param env - 可选的附加环境变量。
# @param input_data - 可选的标准输入字节。
# @param check - 是否将非零退出码视为错误。
# @returns 已完成进程对象。
def run(
    command: Sequence[str],
    *,
    env: dict[str, str] | None = None,
    input_data: bytes | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    completed = subprocess.run(
        list(command),
        input=input_data,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=process_env,
        check=False,
    )
    if check and completed.returncode != 0:
        stderr = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"命令执行失败 ({completed.returncode}): {' '.join(command)}\n{stderr}")
    return completed


# 读取 SVN URL 在仓库中的路径、仓库 UUID 和当前 HEAD 修订号。
# @param svn_url - SVN 目录 URL。
# @returns 仓库相对路径、UUID 与 HEAD 修订号；仓库根路径为空字符串。
def get_svn_repository_info(svn_url: str) -> tuple[str, str, int]:
    result = run(["svn", "info", "--xml", "-r", "HEAD", svn_url])
    root = ET.fromstring(result.stdout)
    entry = root.find("./entry")
    relative_url = entry.findtext("relative-url") if entry is not None else None
    repository_uuid = (
        entry.findtext("./repository/uuid") if entry is not None else None
    )
    head_revision = entry.attrib.get("revision") if entry is not None else None
    if (
        relative_url is None
        or not relative_url.startswith("^")
        or not repository_uuid
        or head_revision is None
    ):
        raise RuntimeError("无法从 svn info 确定 SVN 仓库路径、UUID 或 HEAD 修订号")
    return (
        urllib.parse.unquote(relative_url[1:]).rstrip("/"),
        repository_uuid,
        int(head_revision),
    )


# 将命令行修订参数解析为包含两端的同步范围。
# @param args - 已校验的命令行参数。
# @param head_revision - 目标 SVN URL 当前 HEAD 修订号。
# @returns 起始修订号和结束修订号。
def resolve_revision_range(
    args: argparse.Namespace, head_revision: int
) -> tuple[int, int]:
    if args.revision:
        start = args.revision[0]
        end = args.revision[1] if len(args.revision) == 2 else head_revision
    else:
        start = args.start
        end = args.end
    if start > end:
        raise RuntimeError(
            f"修订范围反序：起始修订 r{start} 大于结束修订 r{end}"
        )
    return start, end


# 将 SVN 日志路径转换为同步树中的相对路径。
# @param changed_path - svn log 返回的仓库绝对路径。
# @param repository_path - SVN URL 对应的仓库绝对路径。
# @returns 属于目标 SVN URL 的相对路径，否则返回 None。
def relative_to_target(changed_path: str, repository_path: str) -> str | None:
    normalized = changed_path.rstrip("/") or "/"
    target = repository_path or ""
    if normalized == (target or "/"):
        return ""
    prefix = f"{target}/" if target else "/"
    if not normalized.startswith(prefix):
        return None
    return normalized[len(prefix) :]


# 读取单个 SVN 修订及其目标路径内的变更。
# @param svn_url - 待同步的 SVN 目录 URL。
# @param revision - SVN 修订号。
# @param repository_path - SVN URL 对应的仓库绝对路径。
# @returns 有相关日志时返回修订对象，否则返回 None。
def read_revision(
    svn_url: str, revision: int, repository_path: str
) -> SvnRevision | None:
    result = run(["svn", "log", "--xml", "-v", "-r", str(revision), svn_url])
    root = ET.fromstring(result.stdout)
    logentry = root.find("logentry")
    if logentry is None:
        return None
    changes: list[SvnChange] = []
    for path_node in logentry.findall("./paths/path"):
        relative_path = relative_to_target(path_node.text or "", repository_path)
        if relative_path is None:
            continue
        changes.append(
            SvnChange(
                action=path_node.attrib.get("action", ""),
                kind=path_node.attrib.get("kind", "unknown"),
                relative_path=relative_path,
            )
        )
    return SvnRevision(
        number=int(logentry.attrib["revision"]),
        author=logentry.findtext("author") or "svn",
        date=logentry.findtext("date") or "",
        message=logentry.findtext("msg") or "",
        changes=tuple(changes),
    )


# 判断路径是否位于被排除的顶层目录中。
# @param relative_path - 同步树中的相对路径。
# @param excluded_roots - 被排除的顶层目录集合。
# @returns 路径应排除时返回 True。
def is_excluded(relative_path: str, excluded_roots: set[str]) -> bool:
    if not relative_path:
        return False
    return PurePosixPath(relative_path).parts[0] in excluded_roots


# 为 SVN 相对路径构造带 peg revision 的 URL。
# @param svn_url - SVN 目录 URL。
# @param relative_path - URL 下的文件相对路径。
# @param revision - SVN 修订号。
# @returns 可传给 svn 子命令的 URL。
def revision_url(svn_url: str, relative_path: str, revision: int) -> str:
    encoded_path = urllib.parse.quote(relative_path, safe="/")
    separator = "/" if relative_path else ""
    return f"{svn_url.rstrip('/')}{separator}{encoded_path}@{revision}"


# 查询 SVN 文件是否设置指定属性。
# @param svn_url - SVN 目录 URL。
# @param relative_path - 文件相对路径。
# @param revision - SVN 修订号。
# @param property_name - SVN 属性名。
# @returns 设置属性时返回 True，否则返回 False。
def has_property(
    svn_url: str, relative_path: str, revision: int, property_name: str
) -> bool:
    result = run(
        [
            "svn",
            "propget",
            "--strict",
            "-r",
            str(revision),
            property_name,
            revision_url(svn_url, relative_path, revision),
        ],
        check=False,
    )
    if result.returncode == 0:
        return True
    stderr = result.stderr.decode("utf-8", errors="replace")
    if "W200017" in stderr or "E200000" in stderr:
        return False
    raise RuntimeError(f"读取 {property_name} 失败: {relative_path}\n{stderr.strip()}")


# 读取 SVN 目录在指定修订中的全部文件路径。
# @param svn_url - SVN 目录 URL。
# @param relative_path - 目录相对路径。
# @param revision - SVN 修订号。
# @returns 目录树内文件相对于同步根的路径列表。
def list_directory_files(svn_url: str, relative_path: str, revision: int) -> list[str]:
    result = run(
        [
            "svn",
            "list",
            "--xml",
            "-R",
            "-r",
            str(revision),
            revision_url(svn_url, relative_path, revision),
        ]
    )
    root = ET.fromstring(result.stdout)
    files: list[str] = []
    for entry in root.findall(".//entry"):
        if entry.attrib.get("kind") != "file":
            continue
        name = entry.findtext("name")
        if name:
            files.append(str(PurePosixPath(relative_path, name)))
    return files


# 将 SVN 文件内容和模式写入临时 Git index。
# @param svn_url - SVN 目录 URL。
# @param relative_path - 文件相对路径。
# @param revision - SVN 修订号。
# @param git_env - 包含临时 GIT_INDEX_FILE 的环境变量。
# @returns 写入后的 Git 模式和 blob ID。
def materialize_file(
    svn_url: str,
    relative_path: str,
    revision: int,
    git_env: dict[str, str],
) -> tuple[str, str]:
    content = run(
        [
            "svn",
            "cat",
            "-r",
            str(revision),
            revision_url(svn_url, relative_path, revision),
        ]
    ).stdout
    if has_property(svn_url, relative_path, revision, "svn:special"):
        if not content.startswith(b"link "):
            raise RuntimeError(f"svn:special 文件内容不是符号链接格式: {relative_path}")
        content = content[len(b"link ") :]
        mode = "120000"
    elif has_property(svn_url, relative_path, revision, "svn:executable"):
        mode = "100755"
    else:
        mode = "100644"
    blob = run(
        ["git", "hash-object", "-w", "--stdin"], input_data=content
    ).stdout.decode().strip()
    run(
        ["git", "update-index", "--add", "--cacheinfo", mode, blob, relative_path],
        env=git_env,
    )
    return mode, blob


# 从临时 index 中按字面路径删除一个文件或目录树。
# @param relative_path - 待删除的 Git 相对路径。
# @param git_env - 包含临时 GIT_INDEX_FILE 的环境变量。
# @returns 实际删除的文件路径列表。
def remove_index_path(relative_path: str, git_env: dict[str, str]) -> list[str]:
    result = run(["git", "ls-files", "-z"], env=git_env)
    all_paths = [path.decode("utf-8") for path in result.stdout.split(b"\0") if path]
    prefix = f"{relative_path}/" if relative_path else ""
    paths = [
        path
        for path in all_paths
        if not relative_path or path == relative_path or path.startswith(prefix)
    ]
    for path in paths:
        run(["git", "update-index", "--force-remove", "--", path], env=git_env)
    return paths


# 将一个 SVN 修订应用到临时 Git index。
# @param svn_url - SVN 目录 URL。
# @param revision - 已解析的 SVN 修订。
# @param excluded_roots - 被排除的顶层目录集合。
# @param git_env - 包含临时 GIT_INDEX_FILE 的环境变量。
# @param expected_paths - 记录受影响路径的预期最终模式和 blob ID。
# @returns 修订是否包含至少一个非排除路径变更。
def apply_revision(
    svn_url: str,
    revision: SvnRevision,
    excluded_roots: set[str],
    git_env: dict[str, str],
    expected_paths: dict[str, tuple[str, str] | None],
) -> bool:
    relevant = False
    for change in revision.changes:
        if is_excluded(change.relative_path, excluded_roots):
            continue
        relevant = True
        if change.action == "D":
            removed_paths = remove_index_path(change.relative_path, git_env)
            for path in removed_paths:
                expected_paths[path] = None
            if not removed_paths and change.relative_path:
                expected_paths[change.relative_path] = None
            continue
        if change.action not in {"A", "M"}:
            raise RuntimeError(
                f"r{revision.number} 包含不支持的 SVN 操作 {change.action}: {change.relative_path}"
            )
        if change.kind == "dir":
            if change.action == "A":
                for path in list_directory_files(
                    svn_url, change.relative_path, revision.number
                ):
                    if is_excluded(path, excluded_roots):
                        continue
                    expected_paths[path] = materialize_file(
                        svn_url, path, revision.number, git_env
                    )
            continue
        if not change.relative_path:
            continue
        expected_paths[change.relative_path] = materialize_file(
            svn_url, change.relative_path, revision.number, git_env
        )
    return relevant


# 以 SVN 元数据创建 Git 提交对象。
# @param tree - 新提交的 Git tree ID。
# @param parent - 父 Git commit ID。
# @param revision - SVN 修订元数据。
# @param repository_uuid - SVN 仓库 UUID。
# @returns 新 Git commit ID。
def create_commit(
    tree: str, parent: str, revision: SvnRevision, repository_uuid: str
) -> str:
    author = revision.author.strip() or "svn"
    identity_env = {
        "GIT_AUTHOR_NAME": author,
        "GIT_AUTHOR_EMAIL": f"{author}@{repository_uuid}",
        "GIT_AUTHOR_DATE": revision.date,
        "GIT_COMMITTER_NAME": author,
        "GIT_COMMITTER_EMAIL": f"{author}@{repository_uuid}",
        "GIT_COMMITTER_DATE": revision.date,
    }
    result = run(
        ["git", "commit-tree", tree, "-p", parent],
        env=identity_env,
        input_data=revision.message.encode("utf-8"),
    )
    return result.stdout.decode().strip()


# 读取 Git 提交中的全部文件模式和对象 ID。
# @param commit - 待读取的 Git commit ID。
# @returns 以字面路径为键、模式和对象 ID 为值的映射。
def read_git_tree(commit: str) -> dict[str, tuple[str, str]]:
    result = run(["git", "ls-tree", "-r", "-z", commit])
    entries: dict[str, tuple[str, str]] = {}
    for record in result.stdout.split(b"\0"):
        if not record:
            continue
        metadata, raw_path = record.split(b"\t", 1)
        mode, _object_type, object_id = metadata.decode("ascii").split(" ", 2)
        entries[raw_path.decode("utf-8")] = (mode, object_id)
    return entries


# 读取本地分支当前提交。
# @param branch - 本地分支短名称。
# @returns 完整引用名和 commit ID。
def resolve_local_branch(branch: str) -> tuple[str, str]:
    run(["git", "check-ref-format", "--branch", branch])
    full_ref = f"refs/heads/{branch}"
    result = run(["git", "rev-parse", "--verify", f"{full_ref}^{{commit}}"])
    return full_ref, result.stdout.decode().strip()


# 确认待移动目标分支未被任何工作树检出。
# @param target_ref - 目标分支完整引用名。
# @returns 无返回值；被检出时抛出 RuntimeError。
def ensure_not_checked_out(target_ref: str) -> None:
    result = run(["git", "worktree", "list", "--porcelain"])
    checked_out = {
        line.removeprefix("branch ")
        for line in result.stdout.decode("utf-8", errors="replace").splitlines()
        if line.startswith("branch ")
    }
    if target_ref in checked_out:
        raise RuntimeError(
            f"合并目标正在工作树中检出，拒绝直接移动引用: {target_ref}"
        )


# 在创建或移动引用前验证候选历史及受影响路径。
# @param base_ref - 用户指定的 Git 基线引用。
# @param base_commit - 开始同步时解析出的基线 commit ID。
# @param candidate - 构造完成的候选分支 tip。
# @param created - 本次创建的提交数。
# @param expected_paths - 受影响路径的最终预期状态。
# @param new_ref - 可选的待创建分支完整引用名。
# @param merge_state - 可选的合并目标引用名和原 commit ID。
# @returns 无返回值；验证失败时抛出 RuntimeError。
def verify_candidate(
    base_ref: str,
    base_commit: str,
    candidate: str,
    created: int,
    expected_paths: dict[str, tuple[str, str] | None],
    new_ref: str | None,
    merge_state: tuple[str, str] | None,
) -> None:
    current_base = run(
        ["git", "rev-parse", "--verify", f"{base_ref}^{{commit}}"]
    ).stdout.decode().strip()
    if current_base != base_commit:
        raise RuntimeError(f"构造期间基线引用发生变化: {base_ref}")
    if new_ref and run(
        ["git", "show-ref", "--verify", "--quiet", new_ref], check=False
    ).returncode == 0:
        raise RuntimeError(f"构造期间目标分支已被创建: {new_ref}")
    if run(
        ["git", "merge-base", "--is-ancestor", base_commit, candidate], check=False
    ).returncode != 0:
        raise RuntimeError("候选历史没有从指定基线线性延伸")
    total_count = int(
        run(["git", "rev-list", "--count", candidate, f"^{base_commit}"]).stdout
    )
    first_parent_count = int(
        run(
            ["git", "rev-list", "--first-parent", "--count", candidate, f"^{base_commit}"]
        ).stdout
    )
    if total_count != created or first_parent_count != created:
        raise RuntimeError(
            f"候选提交数验证失败: expected={created}, total={total_count}, first-parent={first_parent_count}"
        )
    actual_paths = read_git_tree(candidate)
    for path, expected in expected_paths.items():
        actual = actual_paths.get(path)
        if actual != expected:
            raise RuntimeError(
                f"候选路径验证失败: {path}, expected={expected}, actual={actual}"
            )
    if merge_state:
        merge_ref, old_merge_commit = merge_state
        current_merge = run(
            ["git", "rev-parse", "--verify", f"{merge_ref}^{{commit}}"]
        ).stdout.decode().strip()
        if current_merge != old_merge_commit:
            raise RuntimeError(f"构造期间合并目标发生变化: {merge_ref}")
        if run(
            ["git", "merge-base", "--is-ancestor", old_merge_commit, candidate],
            check=False,
        ).returncode != 0:
            raise RuntimeError(
                f"合并目标无法快进到候选历史，需要人工确认 merge commit: {merge_ref}"
            )


# 原子创建同步分支和/或快进合并目标。
# @param candidate - 已验证的候选 commit ID。
# @param new_ref - 可选的新分支完整引用名。
# @param merge_state - 可选的合并目标引用名和 expected-old commit ID。
# @returns 无返回值。
def update_refs(
    candidate: str,
    new_ref: str | None,
    merge_state: tuple[str, str] | None,
) -> None:
    commands = ["start"]
    if new_ref:
        commands.append(f"create {new_ref} {candidate}")
    if merge_state:
        merge_ref, old_merge_commit = merge_state
        commands.append(f"update {merge_ref} {candidate} {old_merge_commit}")
    commands.extend(["prepare", "commit", ""])
    run(["git", "update-ref", "--stdin"], input_data="\n".join(commands).encode("ascii"))


# 执行同步并在验证通过后原子更新目标引用。
# @param args - 已校验的命令行参数。
# @returns 创建的 Git 提交数量。
def synchronize(args: argparse.Namespace) -> int:
    inside = run(["git", "rev-parse", "--is-inside-work-tree"]).stdout.decode().strip()
    if inside != "true":
        raise RuntimeError("当前目录不在 Git 工作树中")
    base_commit = run(
        ["git", "rev-parse", "--verify", f"{args.base_ref}^{{commit}}"]
    ).stdout.decode().strip()

    new_ref: str | None = None
    if args.new_branch:
        run(["git", "check-ref-format", "--branch", args.new_branch])
        new_ref = f"refs/heads/{args.new_branch}"
        if run(
            ["git", "show-ref", "--verify", "--quiet", new_ref], check=False
        ).returncode == 0:
            raise RuntimeError(f"目标分支已存在: {args.new_branch}")

    merge_state: tuple[str, str] | None = None
    if args.merge_target:
        status = run(["git", "status", "--porcelain=v1", "--untracked-files=normal"])
        if status.stdout:
            raise RuntimeError("工作区或 index 不干净，拒绝移动合并目标")
        merge_state = resolve_local_branch(args.merge_target)
        ensure_not_checked_out(merge_state[0])

    repository_path, repository_uuid, head_revision = get_svn_repository_info(
        args.svn_url
    )
    start_revision, end_revision = resolve_revision_range(args, head_revision)
    excluded_roots = set(args.exclude_root)
    expected_paths: dict[str, tuple[str, str] | None] = {}
    parent = base_commit
    created = 0
    with tempfile.TemporaryDirectory(prefix="svn-git-sync-") as temp_dir:
        git_env = {"GIT_INDEX_FILE": os.path.join(temp_dir, "index")}
        run(["git", "read-tree", parent], env=git_env)
        for number in range(start_revision, end_revision + 1):
            revision = read_revision(args.svn_url, number, repository_path)
            if revision is None:
                continue
            relevant = apply_revision(
                args.svn_url,
                revision,
                excluded_roots,
                git_env,
                expected_paths,
            )
            if not relevant:
                continue
            tree = run(["git", "write-tree"], env=git_env).stdout.decode().strip()
            parent = create_commit(tree, parent, revision, repository_uuid)
            created += 1

    verify_candidate(
        args.base_ref,
        base_commit,
        parent,
        created,
        expected_paths,
        new_ref,
        merge_state,
    )
    update_refs(parent, new_ref, merge_state)
    destinations = [value for value in (args.new_branch, args.merge_target) if value]
    print(f"已更新本地引用 {', '.join(destinations)}，包含 {created} 个 SVN 修订提交。")
    return created


# 程序入口，统一输出用户可读错误。
# @param argv - 不含程序名的命令行参数；为 None 时读取 sys.argv。
# @returns 成功时返回 0，失败时返回 1。
def main(argv: Sequence[str] | None = None) -> int:
    try:
        synchronize(parse_args(argv))
        return 0
    except (RuntimeError, ET.ParseError, OSError, ValueError) as error:
        print(f"错误: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
