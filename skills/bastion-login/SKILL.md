---
# @author Codex (gpt-5.6-sol)
name: bastion-login
description: 通过 macOS 可见 Terminal.app 认证公司 JumpServer，并在 Codex 自有 PTY 中安全复用 identity-bound SSH ControlMaster 登录用户明确指定的目标主机。当用户说“堡垒机登录”“JumpServer 登录”“登录某 IP”“复用堡垒机 socket”“检查堡垒机会话”或要求对目标机执行巡检及明确授权的运维操作时使用；不得读取、保存或代填密码、MFA、私钥。
---

# 堡垒机登录

使用 `scripts/iterm2_bastion.sh` 的 `auth/check/status/session` 四个入口。文件名为历史兼容名称；流程不控制 iTerm2、Ghostty 或其他终端。

## 安全边界

- 固定公司入口 `jms.tuniu.org:2222`；用户名使用 `BASTION_USER`，未设置时使用 `whoami`。
- socket 根目录默认使用短路径 `/tmp/codex-bastion-$(id -u)`，可通过 `BASTION_SOCKET_DIR` 覆盖；目录保持当前用户私有 0700，文件名绑定 `user@host:port` 哈希，脚本验证目录和 socket 的类型、owner、mode。
- 不要把默认路径改回较长的 `${TMPDIR}`：OpenSSH 创建 ControlMaster 临时 listener 时会追加后缀，可能超过 macOS Unix socket 路径长度限制。
- 仅 `auth` 可认证，并且必须在可见 Terminal.app 中由用户亲自输入密码/MFA、查看并确认未知主机 fingerprint。
- 不硬编码某次 fingerprint，不自动接受未知 host key，不读取、保存、输出或代填任何凭据。
- `check/status/session` 强制 fail-closed。socket 不存在或失效时停止并提示 `auth`；不得另开普通 SSH、不得后台认证。

## 标准流程

### 1. 检查认证状态

```bash
scripts/iterm2_bastion.sh status
scripts/iterm2_bastion.sh check
```

两者只检查 identity-bound 本地 socket。`inactive` 是预期的未认证状态，不得因此尝试隐藏 SSH。

### 2. 让用户在可见终端认证

仅当 socket 不可用且用户要求继续时运行：

```bash
scripts/iterm2_bastion.sh auth
```

`auth` 打开可见 Terminal.app，使用 `HostKeyAlgorithms=+ssh-rsa`、`StrictHostKeyChecking=ask` 和 `ControlPersist=10m`。让用户亲自确认首次或变化后的主机 fingerprint，并亲自输入密码/MFA。用户确认认证完成后，再运行 `check`；不得读取 Terminal 内容寻找密码或认证信息。

### 3. 在 Codex PTY 中复用会话

确认 `check` 成功后，用 `exec_command` 的 `tty: true` 启动：

```bash
scripts/iterm2_bastion.sh session
```

`session` 在调用者 PTY 中执行 `ssh -tt`，强制 `BatchMode=yes`、`StrictHostKeyChecking=yes`，并禁用密码、键盘交互、公钥、GSSAPI 和 hostbased 直接认证。即使 socket 在检查后失效，也只能快速失败，不能回退为认证连接。

### 4. 选择明确目标

1. 持续读取 PTY 输出，必须看到 JumpServer 的 `Opt>` 或等价目标选择提示后才输入。
2. 目标必须来自用户本轮明确提供的 IP/hostname。输入前检查：匹配 `^[A-Za-z0-9._:-]+$`、不以 `-` 开头、与用户原值完全一致；不得猜测、模糊检索、自动补全或沿用其他任务目标。
3. 使用 `write_stdin` 向同一 PTY 写入目标并附加回车 `\r`，不要新开终端或 SSH。
4. 若出现多个匹配、二次确认、权限拒绝或认证提示，立即停止并让用户处理。
5. 确认出现目标机 shell 后，若用户只要求连接，最多执行 `hostname; whoami; pwd` 做只读身份核验。

## 执行巡检或变更

未获本轮明确授权时，只执行与请求直接相关的只读命令。任何配置修改、服务控制、清理、安装等有状态操作必须同时明确目标主机和动作。

执行已授权变更前，先只读核对主机、账户、路径、当前值和影响范围；说明预期影响并创建可恢复备份。只做最小修改，随后执行匹配的只读验证。遇到目标歧义、认证提示或授权范围不足时停止，不扩大操作或自行回滚。
