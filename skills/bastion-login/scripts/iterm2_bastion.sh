#!/usr/bin/env bash
# @author Codex (gpt-5.6-sol)
set -euo pipefail

readonly JUMP_HOST="jms.tuniu.org"
readonly JUMP_PORT="2222"
readonly JUMP_USER="${BASTION_USER:-$(whoami)}"
readonly JUMP_DESTINATION="${JUMP_USER}@${JUMP_HOST}"
readonly CONTROL_ROOT="${BASTION_SOCKET_DIR:-/tmp/codex-bastion-$(id -u)}"
CONTROL_DIR=""
CONTROL_SOCKET=""

# /**
#  * 输出脚本用法并以参数错误状态退出。
#  *
#  * @param 无 - 不接收函数参数
#  * @returns 不返回，始终以状态码 64 退出
#  */
usage() {
  cat >&2 <<'USAGE'
Usage:
  iterm2_bastion.sh auth
  iterm2_bastion.sh check
  iterm2_bastion.sh status
  iterm2_bastion.sh session

auth opens visible Terminal.app authentication. check/status only inspect the
identity-bound local ControlMaster socket. session must run in a caller-owned
TTY and refuses interactive or key authentication if the socket cannot be used.
USAGE
  exit 64
}

# /**
#  * 读取文件的数字 UID，兼容 macOS 和 GNU stat。
#  *
#  * @param $1 - 要检查的文件路径
#  * @returns 在标准输出中返回数字 UID
#  */
stat_uid() {
  stat -f '%u' "$1" 2>/dev/null || stat -c '%u' "$1" 2>/dev/null
}

# /**
#  * 读取文件的八进制权限，兼容 macOS 和 GNU stat。
#  *
#  * @param $1 - 要检查的文件路径
#  * @returns 在标准输出中返回不带前导零的权限值
#  */
stat_mode() {
  stat -f '%Lp' "$1" 2>/dev/null || stat -c '%a' "$1" 2>/dev/null
}

# /**
#  * 根据固定 JumpServer identity 生成私有目录和 socket 路径。
#  *
#  * @param 无 - 使用固定 host/port 与 BASTION_USER 或 whoami
#  * @returns 设置 CONTROL_DIR 和 CONTROL_SOCKET 后返回 0
#  */
initialize_paths() {
  local identity_hash
  [[ "$JUMP_USER" =~ ^[A-Za-z0-9._-]+$ && "$JUMP_USER" != -* ]] || {
    echo "Invalid BASTION_USER: $JUMP_USER" >&2
    return 64
  }
  [[ "$CONTROL_ROOT" == /* && "$CONTROL_ROOT" != "/" ]] || {
    echo "BASTION_SOCKET_DIR must be a non-root absolute path: $CONTROL_ROOT" >&2
    return 64
  }
  identity_hash=$(printf '%s' "$JUMP_USER@$JUMP_HOST:$JUMP_PORT" | shasum -a 256 | awk '{print substr($1, 1, 16)}')
  [[ "$identity_hash" =~ ^[0-9a-f]{16}$ ]] || {
    echo "Unable to derive JumpServer identity hash." >&2
    return 1
  }
  CONTROL_DIR="${CONTROL_ROOT%/}"
  CONTROL_SOCKET="$CONTROL_DIR/jms-$identity_hash.sock"
}

# /**
#  * 创建或验证当前用户私有的 0700 ControlMaster 目录。
#  *
#  * @param $1 - 传入 create 时允许创建不存在的目录，否则仅验证
#  * @returns 目录安全时返回 0，不存在或 owner/mode 不符时返回非 0
#  */
validate_control_dir() {
  local action="${1:-check}" directory_uid directory_mode current_uid
  current_uid=$(id -u)
  if [[ ! -e "$CONTROL_DIR" ]]; then
    [[ "$action" == "create" ]] || return 1
    (umask 077 && mkdir -m 700 "$CONTROL_DIR")
  fi
  [[ -d "$CONTROL_DIR" && ! -L "$CONTROL_DIR" ]] || {
    echo "Refusing unsafe ControlMaster directory: $CONTROL_DIR" >&2
    return 1
  }
  directory_uid=$(stat_uid "$CONTROL_DIR")
  directory_mode=$(stat_mode "$CONTROL_DIR")
  [[ "$directory_uid" == "$current_uid" ]] || {
    echo "ControlMaster directory is not owned by uid $current_uid: $CONTROL_DIR" >&2
    return 1
  }
  [[ "$directory_mode" == "700" ]] || {
    echo "ControlMaster directory must have mode 700: $CONTROL_DIR ($directory_mode)" >&2
    return 1
  }
}

# /**
#  * 验证 identity-bound socket 的类型、属主及私有权限。
#  *
#  * @param 无 - 使用 initialize_paths 生成的 socket 路径
#  * @returns socket 安全时返回 0，否则返回非 0
#  */
validate_socket() {
  local socket_uid socket_mode current_uid
  validate_control_dir check || return 1
  [[ -S "$CONTROL_SOCKET" && ! -L "$CONTROL_SOCKET" ]] || return 1
  current_uid=$(id -u)
  socket_uid=$(stat_uid "$CONTROL_SOCKET")
  socket_mode=$(stat_mode "$CONTROL_SOCKET")
  [[ "$socket_uid" == "$current_uid" ]] || {
    echo "ControlMaster socket is not owned by uid $current_uid: $CONTROL_SOCKET" >&2
    return 1
  }
  (( (8#$socket_mode & 077) == 0 )) || {
    echo "ControlMaster socket exposes group/other permissions: $CONTROL_SOCKET ($socket_mode)" >&2
    return 1
  }
}

# /**
#  * 仅通过本地 socket 检查固定 JumpServer 的已认证 master。
#  *
#  * @param 无 - 不接收函数参数
#  * @returns live master 存在时返回 0，否则返回非 0
#  */
check_master() {
  validate_socket || return 1
  ssh -S "$CONTROL_SOCKET" -O check \
    -o BatchMode=yes \
    -o StrictHostKeyChecking=yes \
    -o HostKeyAlgorithms=+ssh-rsa \
    -p "$JUMP_PORT" \
    "$JUMP_DESTINATION" >/dev/null 2>&1
}

# /**
#  * 在可见 Terminal.app 中启动由用户亲自处理的交互认证。
#  *
#  * @param 无 - 不接收函数参数
#  * @returns 已有 master 时返回 0，否则返回打开 Terminal.app 的结果
#  */
authenticate_master() {
  local command
  validate_control_dir create || return
  if check_master; then
    echo "Live ControlMaster: $CONTROL_SOCKET ($JUMP_DESTINATION:$JUMP_PORT)"
    return 0
  fi
  if [[ -e "$CONTROL_SOCKET" ]]; then
    echo "Stale or invalid socket exists; inspect it manually: $CONTROL_SOCKET" >&2
    return 1
  fi
  [[ -d /System/Applications/Utilities/Terminal.app ]] || {
    echo "Terminal.app is unavailable." >&2
    return 1
  }
  printf -v command 'umask 077; exec ssh -M -S %q -o ControlPersist=10m -o HostKeyAlgorithms=+ssh-rsa -o StrictHostKeyChecking=ask -p %q %q' \
    "$CONTROL_SOCKET" "$JUMP_PORT" "$JUMP_DESTINATION"
  echo "Opening visible Terminal.app authentication for $JUMP_DESTINATION:$JUMP_PORT. Confirm any unknown host fingerprint and enter credentials only there."
  osascript - "$command" <<'APPLESCRIPT'
-- /**
--  * 在可见 Terminal.app 标签页启动认证命令。
--  *
--  * @param argv - 第一项为已转义的 SSH 命令
--  * @returns 返回新建的 Terminal 标签页
--  */
on run argv
  tell application "Terminal"
    activate
    do script (item 1 of argv)
  end tell
end run
APPLESCRIPT
}

# /**
#  * 在调用者 PTY 中复用 live socket 打开 JumpServer 交互会话。
#  *
#  * @param 无 - 不接收函数参数
#  * @returns 成功时以 SSH 会话替换当前进程，socket 无效时返回非 0
#  */
open_session() {
  if ! check_master; then
    echo "No live identity-bound ControlMaster. Run auth and complete authentication in visible Terminal.app first." >&2
    return 1
  fi
  [[ -t 0 && -t 1 ]] || {
    echo "session requires a caller-owned interactive TTY." >&2
    return 1
  }
  exec ssh -tt \
    -S "$CONTROL_SOCKET" \
    -o ControlMaster=no \
    -o ProxyCommand=/usr/bin/false \
    -o BatchMode=yes \
    -o StrictHostKeyChecking=yes \
    -o HostKeyAlgorithms=+ssh-rsa \
    -o PasswordAuthentication=no \
    -o KbdInteractiveAuthentication=no \
    -o PubkeyAuthentication=no \
    -o GSSAPIAuthentication=no \
    -o HostbasedAuthentication=no \
    -o PreferredAuthentications=none \
    -o NumberOfPasswordPrompts=0 \
    -o ConnectionAttempts=1 \
    -o ConnectTimeout=2 \
    -p "$JUMP_PORT" \
    "$JUMP_DESTINATION"
}

[[ $# -eq 1 ]] || usage
initialize_paths

case "$1" in
  auth)
    authenticate_master
    ;;
  check)
    if check_master; then
      echo "Live ControlMaster: $CONTROL_SOCKET ($JUMP_DESTINATION:$JUMP_PORT)"
    else
      echo "No live ControlMaster: $CONTROL_SOCKET ($JUMP_DESTINATION:$JUMP_PORT)" >&2
      exit 1
    fi
    ;;
  status)
    if check_master; then
      echo "live $CONTROL_SOCKET $JUMP_DESTINATION:$JUMP_PORT"
    else
      echo "inactive $CONTROL_SOCKET $JUMP_DESTINATION:$JUMP_PORT"
      exit 1
    fi
    ;;
  session)
    open_session
    ;;
  *)
    usage
    ;;
esac
