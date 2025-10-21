#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 中文格式化工具
功能：
1. 在英文/数字和中文之间添加空格
2. 将半角标点转换为全角标点（在中文环境中）
3. 移除英文/数字和全角标点之间的空格
4. 为中文句子添加句号（如果需要）
"""

import re
import os
import sys
from pathlib import Path


class MarkdownFormatter:
    def __init__(self):
        # 半角到全角标点的映射
        self.punctuation_map = {
            ',': '，',
            '.': '。',
            '?': '？',
            '!': '！',
            ':': '：',
            ';': '；',
        }

        # 中文字符的正则表达式
        self.chinese_pattern = r'[\u4e00-\u9fff]'
        # 英文和数字的正则表达式
        self.english_pattern = r'[a-zA-Z0-9]'

    def is_in_code_block(self, lines, line_index):
        """检查指定行是否在代码块中"""
        in_code_block = False
        for i in range(line_index + 1):
            if lines[i].strip().startswith('```'):
                in_code_block = not in_code_block
        return in_code_block

    def process_inline_elements(self, text):
        """
        处理行内元素，保护代码、链接等不被修改
        返回：(处理后的文本, 占位符映射)
        """
        placeholders = {}
        placeholder_counter = 0

        # 保护 HTML 实体（如 &emsp;, &nbsp;, &lt;, &gt; 等）
        def replace_entity(match):
            nonlocal placeholder_counter
            placeholder = f"__ENTITY_PLACEHOLDER_{placeholder_counter}__"
            placeholders[placeholder] = match.group(0)
            placeholder_counter += 1
            return placeholder

        text = re.sub(r'&[a-zA-Z0-9#]+;', replace_entity, text)

        # 保护行内代码 `...`
        def replace_code(match):
            nonlocal placeholder_counter
            placeholder = f"__CODE_PLACEHOLDER_{placeholder_counter}__"
            placeholders[placeholder] = match.group(0)
            placeholder_counter += 1
            return placeholder

        text = re.sub(r'`[^`]+`', replace_code, text)

        # 保护链接 [...](...) 和 ![...](...)
        def replace_link(match):
            nonlocal placeholder_counter
            placeholder = f"__LINK_PLACEHOLDER_{placeholder_counter}__"
            placeholders[placeholder] = match.group(0)
            placeholder_counter += 1
            return placeholder

        text = re.sub(r'!?\[([^\]]+)\]\(([^)]+)\)', replace_link, text)

        # 保护 HTML 标签
        def replace_html(match):
            nonlocal placeholder_counter
            placeholder = f"__HTML_PLACEHOLDER_{placeholder_counter}__"
            placeholders[placeholder] = match.group(0)
            placeholder_counter += 1
            return placeholder

        text = re.sub(r'<[^>]+>', replace_html, text)

        # 保护 URL
        def replace_url(match):
            nonlocal placeholder_counter
            placeholder = f"__URL_PLACEHOLDER_{placeholder_counter}__"
            placeholders[placeholder] = match.group(0)
            placeholder_counter += 1
            return placeholder

        text = re.sub(r'https?://[^\s]+', replace_url, text)

        return text, placeholders

    def restore_placeholders(self, text, placeholders):
        """恢复占位符为原始内容"""
        for placeholder, original in placeholders.items():
            text = text.replace(placeholder, original)
        return text

    def add_space_between_chinese_and_english(self, text):
        """在中文和英文/数字之间添加空格"""
        # 中文后面跟英文/数字，且中间没有空格
        text = re.sub(
            f'({self.chinese_pattern})({self.english_pattern})',
            r'\1 \2',
            text
        )
        # 英文/数字后面跟中文，且中间没有空格
        text = re.sub(
            f'({self.english_pattern})({self.chinese_pattern})',
            r'\1 \2',
            text
        )
        return text

    def convert_punctuation_to_fullwidth(self, text):
        """
        将中文环境中的半角标点转换为全角标点
        只转换前后有中文字符的标点
        """
        # 为了避免误转换（如代码中的标点），我们需要确保标点周围有中文
        for half, full in self.punctuation_map.items():
            # 中文 + 半角标点 -> 中文 + 全角标点
            text = re.sub(
                f'({self.chinese_pattern}){re.escape(half)}',
                f'\\1{full}',
                text
            )
            # 半角标点 + 中文 -> 全角标点 + 中文
            text = re.sub(
                f'{re.escape(half)}({self.chinese_pattern})',
                f'{full}\\1',
                text
            )
            # 半角标点在两个中文字符之间
            text = re.sub(
                f'({self.chinese_pattern}){re.escape(half)}({self.chinese_pattern})',
                f'\\1{full}\\2',
                text
            )

        # 特殊处理：句子末尾的半角标点
        # 如果一行以中文字符后跟半角标点结尾，转换为全角
        for half, full in self.punctuation_map.items():
            text = re.sub(
                f'({self.chinese_pattern}){re.escape(half)}\\s*$',
                f'\\1{full}',
                text,
                flags=re.MULTILINE
            )

        return text

    def remove_space_before_fullwidth_punctuation(self, text):
        """移除英文/数字和全角标点之间的空格"""
        fullwidth_punctuations = ''.join(self.punctuation_map.values())
        # 英文/数字 + 空格 + 全角标点 -> 英文/数字 + 全角标点
        text = re.sub(
            f'({self.english_pattern})\\s+([{fullwidth_punctuations}])',
            r'\1\2',
            text
        )
        return text

    def format_line(self, line, lines, line_index):
        """格式化单行文本"""
        # 跳过代码块
        if self.is_in_code_block(lines, line_index):
            return line

        # 跳过空行
        if not line.strip():
            return line

        # 保护行内元素
        processed_line, placeholders = self.process_inline_elements(line)

        # 应用格式化规则
        # 1. 添加中英文之间的空格
        processed_line = self.add_space_between_chinese_and_english(processed_line)

        # 2. 转换半角标点为全角标点
        processed_line = self.convert_punctuation_to_fullwidth(processed_line)

        # 3. 移除英文/数字和全角标点之间的空格
        processed_line = self.remove_space_before_fullwidth_punctuation(processed_line)

        # 恢复占位符
        processed_line = self.restore_placeholders(processed_line, placeholders)

        return processed_line

    def format_file(self, file_path):
        """格式化单个 Markdown 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            formatted_lines = []

            for i, line in enumerate(lines):
                formatted_line = self.format_line(line, lines, i)
                formatted_lines.append(formatted_line)

            formatted_content = '\n'.join(formatted_lines)

            # 只有当内容发生变化时才写入
            if formatted_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                return True, "已格式化"
            else:
                return False, "无需修改"

        except Exception as e:
            return False, f"错误: {str(e)}"

    def format_directory(self, directory, recursive=True):
        """格式化目录下的所有 Markdown 文件"""
        results = []

        if recursive:
            pattern = '**/*.md'
        else:
            pattern = '*.md'

        md_files = list(Path(directory).glob(pattern))

        print(f"找到 {len(md_files)} 个 Markdown 文件")
        print("-" * 80)

        for file_path in md_files:
            modified, status = self.format_file(file_path)
            relative_path = file_path.relative_to(directory)
            results.append((relative_path, modified, status))

            # 打印进度
            status_symbol = "✓" if modified else "○"
            print(f"{status_symbol} {relative_path}: {status}")

        print("-" * 80)

        # 统计
        modified_count = sum(1 for _, modified, _ in results if modified)
        print(f"\n总计: {len(results)} 个文件, {modified_count} 个已修改")

        return results


def main():
    """主函数"""
    # 默认处理当前目录
    directory = os.getcwd()

    # 如果提供了命令行参数，使用指定目录
    if len(sys.argv) > 1:
        directory = sys.argv[1]

    if not os.path.isdir(directory):
        print(f"错误: {directory} 不是一个有效的目录")
        sys.exit(1)

    print(f"正在格式化目录: {directory}")
    print("=" * 80)

    formatter = MarkdownFormatter()
    formatter.format_directory(directory, recursive=True)


if __name__ == "__main__":
    main()
