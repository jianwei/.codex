# RTK 命令规则（Codex）

RTK（Rust Token Killer）用于压缩 shell 命令输出，减少进入模型上下文的内容。
官方依据：[源码](https://github.com/rtk-ai/rtk)、[完整提示模板](https://github.com/rtk-ai/rtk/blob/v0.50.0/hooks/rtk-awareness-full.md)。

## 执行规则

- 默认给外部命令加 `rtk` 前缀；未匹配过滤器的命令可以透传，但不会因此获得压缩收益。
- shell 内建命令、变量赋值、管道、重定向和 here-document 由当前 shell 解析；保留原有引号和参数边界。需要切换目录时优先使用执行工具的 `workdir`。
- 命令链中的各条外部命令分别加前缀，例如 `rtk git status && rtk git diff --stat`。
- 命令和参数支持以本机 `rtk --help`、`rtk <子命令> --help` 为准。需要确认映射时使用 `rtk rewrite '<原命令>'`，检查输出和退出码。
- RTK 包装后的命令仍须遵循原命令的授权范围和执行限制。

```bash
rtk git status
rtk cargo test
rtk npm run build
rtk pytest -q
rtk pnpm list
```

## 输出与恢复

- 默认使用压缩结果；输出提示完整结果的恢复路径时，按该路径读取所需内容。
- 需要逐字文件内容、机器解析、完整差异，或压缩输出为空、乱码、与退出码矛盾时，使用 `rtk proxy <命令> [参数...]` 获取原始输出并保留使用统计。
- 有副作用的命令优先读取已保存输出或做只读核验；仅为恢复输出而重复执行前，先确认重复执行安全。
- `rtk proxy` 直接执行外部命令；需要指定 shell 语法时，可显式使用 `rtk proxy zsh -c '<脚本>'`。

```bash
rtk proxy cat path/to/file
rtk proxy git diff
rtk proxy rg -n 'pattern' src/
```

## 核验与统计

```bash
rtk --version
rtk --help
rtk proxy which -a rtk
rtk gain
rtk gain --history
```

`rtk gain` 表示命令输出的估算 token 节省量，不等于整体费用的节省比例。升级 RTK 或安装自动改写 hook 属于单独的配置变更，按用户授权执行；手动加前缀不依赖 hook 已安装。
