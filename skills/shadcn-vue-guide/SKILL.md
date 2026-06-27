---
name: shadcn-vue-guide
description: shadcn-vue 通用使用指南——安装、配置、加减组件、自定义风格、多框架适配
whenToUse: 用户询问 shadcn-vue 的安装、配置、组件添加、主题定制、表单集成、多框架适配、或常见问题排查时触发
triggers:
  - 添加 shadcn-vue 组件
  - shadcn-vue 安装/配置/init/add
  - shadcn-vue 表单/主题/自定义
  - shadcn-vue + Nuxt/VuePress
  - 组件库集成问题
---

# shadcn-vue 使用指南

## 是什么

shadcn-vue 不是 npm 包——是 CLI 工具，把组件源码直接拷进项目。你完全掌控：改样式、删代码、修逻辑都自由。

官方：[shadcn-vue.com](https://www.shadcn-vue.com)
GitHub：`shadcn-vue/ui`
底层：基于 **Reka UI**（原 Radix Vue），无头组件 + Tailwind 样式。

---

## 1. 前置条件

| 要求 | 说明 |
|------|------|
| Vue | 3.4+ |
| 框架 | Vite / Nuxt / VuePress / 任意 Vue 3 项目 |
| TypeScript | 推荐，非必须 |
| Tailwind CSS | v4+（强依赖） |

---

## 2. 安装 Tailwind CSS（必须前置）

**Vite 项目：**

```bash
pnpm add tailwindcss @tailwindcss/vite
```

`src/style.css`：

```css
@import "tailwindcss";
```

`vite.config.ts`：

```ts
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
})
```

**Nuxt：**

```bash
npx nuxi module add @nuxtjs/tailwindcss
```

**其他框架：** 先搞定 Tailwind v4 集成，再继续。

---

## 3. components.json（配置中心）

`init` 生成，核心配置：

```json
{
  "$schema": "https://shadcn-vue.com/schema.json",
  "style": "default",
  "typescript": true,
  "tailwind": {
    "css": "src/style.css",
    "baseColor": "neutral",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

> Tailwind v4 不再用 `tailwind.config.js`。`components.json` 中不要配 `tailwind.config` 字段。v3 迁移到 v4 的项目需先移除旧配置文件。

关键字段：

| 字段 | 说明 |
|------|------|
| `style` | `default` / `new-york`（不同视觉风格） |
| `tailwind.cssVariables` | true=CSS 变量主题，false=硬编码颜色 |
| `aliases` | 组件和工具函数导入路径 |

---

## 4. 初始化 CLI

```bash
pnpm dlx shadcn-vue@latest init
```

交互式配置，主要选项：

| 选项 | 推荐值 |
|------|--------|
| Style | Default / New York |
| Base color | Neutral / Zinc / Slate / Stone / Gray |
| CSS variables | Yes |
| tsconfig paths | Yes（自动配 `@/` 别名） |

如果项目已有 `@/` 别名跳过。init 失败时手动配 `vite.config.ts`：

```ts
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

生成文件：
- `components.json` — 组件配置中心
- `src/lib/utils.ts` — `cn()` 工具函数（基于 `clsx` + `tailwind-merge`）
- `src/components/ui/` — 组件目录（刚 init 是空的）

---

## 5. 加减组件

**加组件：**

```bash
# pnpm
pnpm dlx shadcn-vue@latest add button
pnpm dlx shadcn-vue@latest add card dialog
pnpm dlx shadcn-vue@latest add -a       # 加全部

# npm
npx shadcn-vue@latest add button
```

**看可用组件：**

```bash
pnpm dlx shadcn-vue@latest add
# 不加组件名 → 列表
```

**组件物理位置：**

```
src/components/ui/
├── button/
│   ├── Button.vue
│   └── index.ts
├── card/
│   ├── Card.vue
│   └── index.ts
└── dialog/
    ├── Dialog.vue
    ├── DialogClose.vue
    ├── DialogContent.vue
    ├── DialogDescription.vue
    ├── DialogFooter.vue
    ├── DialogHeader.vue
    ├── DialogTitle.vue
    ├── DialogTrigger.vue
    └── index.ts
```

**自定义组件：** 文件就在项目里，直接改。

---

## 6. 使用组件

```vue
<script setup lang="ts">
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
</script>

<template>
  <Card class="w-80">
    <CardHeader>
      <CardTitle>标题</CardTitle>
      <CardDescription>描述文字</CardDescription>
    </CardHeader>
    <CardContent>
      <p>内容区域</p>
    </CardContent>
    <CardFooter>
      <Button variant="outline">取消</Button>
      <Button>提交</Button>
    </CardFooter>
  </Card>
</template>
```

---

## 7. 组件 Props 一览

### Button

| Prop | 类型 | 默认值 |
|------|------|--------|
| variant | `default \| destructive \| outline \| secondary \| ghost \| link` | `default` |
| size | `default \| sm \| lg \| icon` | `default` |
| asChild | `boolean` | `false` |

### Badge

| Prop | 类型 | 默认值 |
|------|------|--------|
| variant | `default \| secondary \| destructive \| outline` | `default` |

### Input

标准 `<input>` 属性透传 + `modelValue` 支持 `v-model`。

### Textarea

同 Input，`<textarea>` 属性 + `modelValue`。

### Dialog

| 组件 | 说明 |
|------|------|
| Dialog | 根组件，`v-model:open` 控制 |
| DialogTrigger | 触发按钮 |
| DialogContent | 弹窗内容 |
| DialogHeader | 头部（可含 DialogTitle + DialogDescription） |
| DialogFooter | 底部操作区 |

### Select

| 组件 | 说明 |
|------|------|
| Select | 根，`v-model` 绑定值 |
| SelectTrigger | 触发区域（显示选中值） |
| SelectValue | 占位符/显示值 |
| SelectContent | 下拉面板 |
| SelectItem | 单个选项，`value` prop |

### Tabs

| 组件 | 说明 |
|------|------|
| Tabs | 根，`defaultValue` 指定默认 tab |
| TabsList | tab 标签容器 |
| TabsTrigger | 单个标签，`value` prop |
| TabsContent | 内容面板，`value` prop |

### Tooltip

| 组件 | 说明 |
|------|------|
| TooltipProvider | 根 |
| Tooltip | 控制显示 |
| TooltipTrigger | 触发元素 |
| TooltipContent | 提示内容 |

### Sonner（Toast）

```bash
pnpm dlx shadcn-vue@latest add sonner
```

```vue
<script setup lang="ts">
import { Toaster } from '@/components/ui/sonner'
import { toast } from 'sonner'
</script>

<template>
  <Toaster />
  <Button @click="toast.success('保存成功')">保存</Button>
</template>
```

---

## 8. 表单集成

shadcn-vue 支持 `useFormField` 组合式函数 + zod 校验：

```bash
pnpm dlx shadcn-vue@latest add form
pnpm add zod @vueuse/core
```

```vue
<script setup lang="ts">
import { z } from 'zod'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'

import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'

const formSchema = z.object({
  username: z.string().min(2).max(50),
})

const { handleSubmit } = useForm({
  validationSchema: toTypedSchema(formSchema),
})

const onSubmit = handleSubmit((values) => {
  console.log(values)
})
</script>
```

---

## 9. 自定义主题

### CSS 变量方式

`components.json` 中 `tailwind.cssVariables: true` 时生效。

```css
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.5 0.2 240);
  --color-destructive: oklch(0.6 0.25 20);
  --radius: 0.5rem;
}
```

OKLCH 颜色优于 HSL。

### Dark Mode

shadcn-vue 通过 `.dark` class 实现暗色模式。两种方案选其一：

**方案 A：全用 `@theme`（Tailwind v4 推荐，一键式，适合大部分项目）**
```css
@import "tailwindcss";

@theme {
  --color-primary: oklch(0.2 0.04 240);
  --color-background: oklch(1 0 0);
}

@theme dark {
  --color-primary: oklch(0.8 0.15 240);
  --color-background: oklch(0.15 0.02 240);
}
```

**方案 B：CSS 变量 + `:root`/`.dark`（传统方式，适合需精细控制的项目）**

```css
@import "tailwindcss";

:root {
  --color-primary: oklch(0.2 0.04 240);
  --color-background: oklch(1 0 0);
}

.dark {
  --color-primary: oklch(0.8 0.15 240);
  --color-background: oklch(0.15 0.02 240);
}
```

切换：

```vue
<script setup lang="ts">
import { useDark, useToggle } from '@vueuse/core'
const isDark = useDark()
const toggleDark = useToggle(isDark)
</script>

<template>
  <Button @click="toggleDark()">{{ isDark ? '🌙' : '☀️' }}</Button>
</template>
```

---

## 10. 内部依赖说明

shadcn-vue 组件 add 时自动安装以下包：

| 包 | 用途 |
|------|------|
| `class-variance-authority` | `cva()` 管理 variant 变体 |
| `clsx` | 条件 class 合并 |
| `tailwind-merge` | 智能合并 Tailwind class |
| `tailwindcss-animate` | 动画工具类 |
| `@vueuse/core` | 部分组件需要 |

`tailwindcss-animate` 需在 CSS 注册：

```css
@import "tailwindcss";
@plugin "tailwindcss-animate";
```

---

## 11. 多框架适配

### Nuxt

```bash
npx nuxi module add @nuxtjs/tailwindcss
pnpm dlx shadcn-vue@latest init
```

SSR 注意：含 `onMounted` 的组件包 `<ClientOnly>`。

### VuePress 2

1. 样式：`docs/.vuepress/styles/index.css` 加 `@import "tailwindcss"`
2. 别名：VuePress 默认 `@vuepress`，init 时手动设 `utils` 和 `components` 路径
3. **仅加基础组件**（button/badge/card/input），交互组件跟主题可能冲突

### 非 Vite 项目

CLI 仅支持 Vite/Nuxt。其他构建工具（webpack/Rollup）手动配 `components.json`，用 `--yes` 跳过检测：

```bash
pnpm dlx shadcn-vue@latest add button --yes
```

---

## 12. 升级组件

重新跑 add，CLI 会问是否覆盖：

```bash
pnpm dlx shadcn-vue@latest add button
# 提示：Button.vue 已存在，覆盖？（Y/n）
```

**推荐做法：**
- 不改原始组件文件
- 用 `class` prop 覆盖样式
- 需要大变时包一层自定义组件

---

## 13. 故障排查表（失败模式）

| 症状 | 原因 | 一线修复 | 仍失败兜底 |
|------|------|---------|-----------|
| Tailwind 类不生效 | CSS 入口缺失或路径不匹配 | 确认 `@import "tailwindcss"` 在 CSS 第一行，且 `components.json` 的 `tailwind.css` 路径指向此文件 | 重启 dev server；确认 `@tailwindcss/vite` 插件在 `vite.config.ts` 的 plugins 数组中 |
| v-model 不工作 | prop 名用错 | Input/Dialog/Select 分别用 `modelValue`/`open`/`modelValue` | 检查组件 `defineProps` 定义 |
| SSR 报错 `window not defined` | 交互组件在 SSR 阶段运行 | 用 `<ClientOnly>` 包裹交互组件 | 组件级 `definePageMeta({ ssr: false })` — 放弃该页 SSR |
| `cva is not defined` error | 缺 `class-variance-authority` 包 | `pnpm add class-variance-authority` | 删除 node_modules 后重新 install |
| 动画/过渡无效 | 缺 `tailwindcss-animate` 插件 | `pnpm add tailwindcss-animate` 并在 CSS 加 `@plugin "tailwindcss-animate"` | 检查插件注册顺序 |
| `@/` 别名找不到 | init 时别名配置失败 | 手动配 vite.config.ts 的 `resolve.alias` | 在 `components.json` 中用相对路径替代 |
| init 卡住或报错 | 项目结构不标准 | 用 `--yes` 跳过检测：`pnpm dlx shadcn-vue@latest init --yes` | 手动创建 `components.json` 后重试 |
| 颜色/主题不按预期 | `@theme` 与 CSS 变量混用 | 选一种方案：要么全 `@theme`，要么全 `:root`/`.dark` CSS 变量 | 检查变量名是否被其他 CSS 覆盖（优先级问题） |

---

## 14. 反例：不要这样做

| 反模式 | 后果 | 正确做法 |
|--------|------|---------|
| 直接改组件源码实现定制 | 升级时覆盖丢失，只能全盘覆盖或手动合 | 用 `class` prop 覆盖样式，大变时包一层自定义组件 |
| 同时用 `@theme` 和 `:root`/`.dark` CSS 变量 | 冲突，部分变量不生效，行为不可预测 | 选一种：Tailwind v4 用 `@theme`，传统 CSS 变量模式用 `:root`/`.dark`。不要混用 |
| `@import "tailwindcss"` 放在 `@theme` 前面 | Tailwind v4 报错，`@theme` 不会生效 | `@import "tailwindcss"` 必须在第一行，`@theme` 在后面 |
| 大版本升级时直接覆盖组件 | 手写定制全部丢失，回退困难 | 不改原始组件；只动上层封装组件 |
| 不加 `@plugin "tailwindcss-animate"` 就用动画组件 | Dialog/Popover 等过渡动画无效果 | CSS 文件加 `@plugin "tailwindcss-animate"` |
| init 后不移除过时的 `tailwind.config.js` | 文件残留但 v4 不使用，配置文件扩散 | 确认 v4 运行正常后删除 |
| Nuxt 里不加 `<ClientOnly>` 直接放交互组件 | SSR 报错 `window is not defined` | 交互组件（Dialog/DropdownMenu/Toast）加 `<ClientOnly>` 包裹 |
| 多个 shadcn-vue 组件共用一个 UI 库 CSS reset | 样式冲突，class 覆盖异常 | shadcn-vue 是本地文件，不依赖外部 UI 包。冲突来自 Tailwind 类同名，加 `@layer` 解决 |
