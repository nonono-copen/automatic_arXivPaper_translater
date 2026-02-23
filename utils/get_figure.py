#!/usr/bin/env python3
"""
ArXiv論文PDFから最も概要図である可能性が高い1枚のみを抽出
Raspberry Pi 4 (4GB) 対応版
"""

import os
import re
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import argparse


class ArxivFigureExtractor:
    """ArXiv論文から最も概要図である可能性が高い図1枚を抽出するクラス"""
    
    def __init__(self, pdf_path: str, output_dir: str = "extracted_figures", dpi: int = 150):
        self.pdf_path = pdf_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.doc = None
        self.dpi = dpi
        
    def open_pdf(self):
        """PDFファイルを開く"""
        try:
            self.doc = fitz.open(self.pdf_path)
            print(f"PDF読み込み成功: {self.pdf_path}")
            print(f"総ページ数: {len(self.doc)}")
        except Exception as e:
            print(f"PDFの読み込みに失敗: {e}")
            raise
    
    def close_pdf(self):
        """PDFファイルを閉じる"""
        if self.doc:
            self.doc.close()
    
    def find_figure_mentions(self, page_num: int) -> List[Dict]:
        """ページから図への言及とキャプションを検出"""
        page = self.doc[page_num]
        text = page.get_text()
        
        figures = []
        
        # Figure X のパターンを検索
        patterns = [
            r'Figure\s+(\d+)[:\.]?\s*([^\n]+(?:\n(?!Figure|Table|\d+\s+[A-Z])[^\n]+)*)',
            r'Fig\.?\s+(\d+)[:\.]?\s*([^\n]+(?:\n(?!Fig\.|Table|\d+\s+[A-Z])[^\n]+)*)',
        ]
        
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
                fig_num = match.group(1)
                caption = match.group(0).strip()
                
                # キャプションの位置を特定
                caption_bbox = self.find_text_bbox(page, match.group(0)[:50])
                
                if caption_bbox:
                    figures.append({
                        'fig_num': fig_num,
                        'caption': caption,
                        'caption_bbox': caption_bbox,
                        'page': page_num
                    })
        
        # 重複を削除（同じ図番号）
        unique_figures = {}
        for fig in figures:
            if fig['fig_num'] not in unique_figures:
                unique_figures[fig['fig_num']] = fig
        
        return list(unique_figures.values())
    
    def find_text_bbox(self, page, search_text: str) -> Optional[fitz.Rect]:
        """テキストの位置を検索"""
        areas = page.search_for(search_text[:30])
        if areas:
            return areas[0]
        return None
    
    def find_all_content_above_caption(self, page_num: int, caption_bbox: fitz.Rect) -> fitz.Rect:
        """キャプションの上にある全てのコンテンツ領域を検出"""
        page = self.doc[page_num]
        page_rect = page.rect
        
        caption_y = caption_bbox.y0
        content_rects = []
        
        # 1. 画像オブジェクトを探す
        image_list = page.get_images(full=True)
        for img in image_list:
            xref = img[0]
            rects = page.get_image_rects(xref)
            for rect in rects:
                if rect.y1 <= caption_y + 20:
                    content_rects.append(rect)
        
        # 2. 描画オブジェクトを探す
        drawings = page.get_drawings()
        for drawing in drawings:
            rect = drawing.get("rect")
            if rect and rect.y1 <= caption_y + 20:
                content_rects.append(rect)
        
        # 3. テキストブロック（図内のラベル）
        text_dict = page.get_text("dict")
        for block in text_dict.get("blocks", []):
            if block.get("type") == 0:
                bbox = block.get("bbox")
                if bbox:
                    block_rect = fitz.Rect(bbox)
                    if block_rect.y1 <= caption_y and not block_rect.intersects(caption_bbox):
                        block_width = block_rect.width
                        page_width = page_rect.width
                        
                        if block_width < page_width * 0.6:
                            content_rects.append(block_rect)
        
        if not content_rects:
            estimated_height = 250
            return fitz.Rect(
                caption_bbox.x0 - 10,
                max(0, caption_y - estimated_height),
                caption_bbox.x1 + 10,
                caption_y
            )
        
        # 全てのコンテンツを含む矩形
        min_x = min(r.x0 for r in content_rects)
        min_y = min(r.y0 for r in content_rects)
        max_x = max(r.x1 for r in content_rects)
        max_y = max(r.y1 for r in content_rects)
        
        margin = 5
        figure_rect = fitz.Rect(
            max(0, min_x - margin),
            max(0, min_y - margin),
            min(page_rect.width, max_x + margin),
            min(caption_y, max_y + margin)
        )
        
        return figure_rect
    
    def calculate_overview_score(self, fig_info: Dict) -> float:
        """図が概要図である可能性をスコアリング（0-100）"""
        score = 0.0
        fig_num = fig_info['fig_num']
        caption = fig_info['caption'].lower()
        page = fig_info['page']
        
        # 1. 図番号によるスコア（最重要）
        if fig_num == '1':
            score += 50  # Figure 1は概要図の可能性が非常に高い
        elif fig_num == '2':
            score += 25  # Figure 2も可能性あり
        elif fig_num == '3':
            score += 10
        else:
            # それ以降は図番号が大きくなるほど減点
            try:
                num = int(fig_num)
                score -= (num - 3) * 2
            except:
                pass
        
        # 2. ページ位置によるスコア
        # 最初の5ページ内にある図は概要図の可能性が高い
        if page <= 2:
            score += 20
        elif page <= 5:
            score += 10
        elif page > 10:
            score -= 10
        
        # 3. キャプション内のキーワードによるスコア
        overview_keywords = {
            'overview': 15,
            'architecture': 12,
            'framework': 12,
            'pipeline': 10,
            'workflow': 10,
            'system': 8,
            'model': 7,
            'approach': 7,
            'method': 6,
            'illustration': 8,
            'schematic': 10,
            'diagram': 8,
            'structure': 7,
            'flow': 6,
            'process': 6,
            'design': 5,
            'proposed': 8,
        }
        
        for keyword, points in overview_keywords.items():
            if keyword in caption:
                score += points
        
        # 4. キャプションの長さによるスコア調整
        # 概要図のキャプションは通常やや長め
        caption_length = len(caption)
        if 100 <= caption_length <= 400:
            score += 5
        elif caption_length > 400:
            score += 2
        
        return max(0, score)  # 負のスコアは0に
    
    def extract_figure_as_image(self, page_num: int, rect: fitz.Rect, fig_num: str, 
                               include_caption: bool = False, 
                               caption_bbox: Optional[fitz.Rect] = None) -> str:
        """指定された領域を画像として抽出"""
        page = self.doc[page_num]
        
        # キャプションを含める場合
        if include_caption and caption_bbox:
            combined_rect = fitz.Rect(
                min(rect.x0, caption_bbox.x0),
                rect.y0,
                max(rect.x1, caption_bbox.x1),
                caption_bbox.y1
            )
            rect = combined_rect
        
        # 解像度の計算
        zoom = self.dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        
        # 指定領域の画像を取得
        pix = page.get_pixmap(matrix=mat, clip=rect)
        
        # 保存
        suffix = "_with_caption" if include_caption else ""
        filename = f"overview_figure_{fig_num}{suffix}_page_{page_num+1}.png"
        filepath = self.output_dir / filename
        pix.save(filepath)
        
        file_size = os.path.getsize(filepath)
        print(f"保存: {filename} ({file_size/1024:.1f} KB, {pix.width}x{pix.height})")
        
        return str(filepath)
    
    def extract_best_overview_figure(self, max_pages: int = 5, include_caption: bool = True) -> str:
        """最も概要図である可能性が高い1枚を抽出"""
        self.open_pdf()
        
        try:
            all_candidates = []
            max_pages = min(max_pages, len(self.doc))
            
            print(f"\n最初の{max_pages}ページを解析中...")
            print(f"解像度: {self.dpi} DPI")
            if include_caption:
                print("モード: キャプションを画像に含める")
            
            # 全ページから図候補を収集
            for page_num in range(max_pages):
                print(f"\nページ {page_num + 1} を処理中...")
                
                figures = self.find_figure_mentions(page_num)
                
                if figures:
                    print(f"  {len(figures)}個の図を発見")
                    
                    for fig_info in figures:
                        # スコアを計算
                        score = self.calculate_overview_score(fig_info)
                        fig_info['score'] = score
                        
                        fig_num = fig_info['fig_num']
                        print(f"  - Figure {fig_num}: スコア {score:.1f}")
                        
                        all_candidates.append(fig_info)
            
            if not all_candidates:
                print("\n図が見つかりませんでした。")
                return
            
            # スコアでソートして最高得点の図を選択
            best_figure = max(all_candidates, key=lambda x: x['score'])
            
            print("\n" + "=" * 60)
            print("最も概要図である可能性が高い図:")
            print(f"  Figure {best_figure['fig_num']} (ページ {best_figure['page'] + 1})")
            print(f"  スコア: {best_figure['score']:.1f}")
            print(f"  キャプション: {best_figure['caption'][:100]}...")
            print("=" * 60)
            
            # 図の領域を特定
            caption_bbox = best_figure['caption_bbox']
            page_num = best_figure['page']
            
            if caption_bbox:
                figure_rect = self.find_all_content_above_caption(page_num, caption_bbox)
                
                if figure_rect.width > 50 and figure_rect.height > 50:
                    print(f"\n領域: {figure_rect.width:.0f}x{figure_rect.height:.0f} (x={figure_rect.x0:.0f}, y={figure_rect.y0:.0f})")
                    
                    # 画像として抽出
                    image_path = self.extract_figure_as_image(
                        page_num, figure_rect, best_figure['fig_num'],
                        include_caption=include_caption,
                        caption_bbox=caption_bbox
                    )
                    
                    # キャプションをテキストファイルに保存
                    caption_file = self.output_dir / f"overview_figure_{best_figure['fig_num']}_caption.txt"
                    with open(caption_file, 'w', encoding='utf-8') as f:
                        f.write(best_figure['caption'])
                    
                    print(f"\n抽出完了！")
                    print(f"出力先: {self.output_dir.absolute()}")
                    
                    # 他の候補も表示
                    if len(all_candidates) > 1:
                        print("\n他の候補:")
                        sorted_candidates = sorted(all_candidates, key=lambda x: x['score'], reverse=True)
                        for i, candidate in enumerate(sorted_candidates[1:6], 2):  # 上位5つまで
                            print(f"  {i}. Figure {candidate['fig_num']} (ページ {candidate['page']+1}, スコア {candidate['score']:.1f})")
                else:
                    print(f"\n警告: 検出された領域が小さすぎます")
            else:
                print(f"\n警告: キャプション位置を特定できませんでした")
            
        finally:
            self.close_pdf()

        return str(os.path.join(self.output_dir.absolute(), image_path))


def main():
    parser = argparse.ArgumentParser(
        description='ArXiv論文PDFから最も概要図である可能性が高い1枚のみを抽出'
    )
    parser.add_argument(
        'pdf_path',
        help='入力PDFファイルのパス'
    )
    parser.add_argument(
        '-o', '--output',
        default='extracted_figures',
        help='出力ディレクトリ（デフォルト: extracted_figures）'
    )
    parser.add_argument(
        '-p', '--max-pages',
        type=int,
        default=10,
        help='解析する最大ページ数（デフォルト: 10）'
    )
    parser.add_argument(
        '--dpi',
        type=int,
        default=150,
        choices=[72, 150, 300],
        help='出力画像の解像度（デフォルト: 150、高品質: 300）'
    )
    parser.add_argument(
        '--include-caption',
        action='store_true',
        help='キャプションも画像に含める'
    )
    
    args = parser.parse_args()
    
    # PDFファイルの存在確認
    if not os.path.exists(args.pdf_path):
        print(f"エラー: ファイルが見つかりません: {args.pdf_path}")
        return
    
    print("=" * 60)
    print("ArXiv 論文概要図抽出ツール（ベスト1枚のみ）")
    print("=" * 60)
    
    # 抽出処理を実行
    extractor   = ArxivFigureExtractor(args.pdf_path, args.output, dpi=args.dpi)
    output_path = extractor.extract_best_overview_figure(args.max_pages, include_caption=args.include_caption)
    print(f"{output_path}")

if __name__ == "__main__":
    main()