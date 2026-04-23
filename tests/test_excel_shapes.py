"""
Excel 파형 내보내기 — 타이밍 도형(선/텍스트상자) 표시 검증 테스트

실행:
    python tests/test_excel_shapes.py
    또는
    pytest tests/test_excel_shapes.py -v
"""

import os
import sys
import zipfile
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))

from excel_waveform_exporter import ExcelWaveformExporter


# ── 공통 테스트 데이터 ───────────────────────────────────────────
SAMPLE_SIGNAL = {
    'num': 'S01', 'name': 'CLK', 'visible': True,
    'v1': 0.0, 'v2': 3.3, 'v3': 0.0, 'v4': 3.3,
    'delay': 10.0, 'width': 40.0, 'period': 100.0,
}


def _export_and_read_drawing_xml(signal: dict, sync_data_us: float = 1000.0) -> str:
    """파형 내보내기 후 xlsx 내부 drawing XML 문자열 반환"""
    exp = ExcelWaveformExporter()
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        path = f.name
    try:
        ok = exp.export(path, [signal], sync_data_us, "TestModel")
        assert ok, "export() 가 False를 반환함"

        with zipfile.ZipFile(path, 'r') as z:
            names = z.namelist()
            drawing_files = [n for n in names if 'drawing' in n and n.endswith('.xml')]
            assert drawing_files, (
                f"xlsx 내부에 drawing XML 파일이 없음!\n"
                f"전체 파일 목록: {names}\n"
                "→ _apply_shapes_to_worksheets 가 ws._drawing 을 제대로 설정하지 못함"
            )
            return z.read(drawing_files[0]).decode('utf-8')
    finally:
        os.unlink(path)


def test_drawing_file_exists():
    """drawing XML 파일이 xlsx 안에 존재하는지 확인"""
    xml = _export_and_read_drawing_xml(SAMPLE_SIGNAL)
    assert xml, "drawing XML이 비어 있음"
    print("[PASS] drawing XML 파일 존재 확인")
    print(f"       XML 크기: {len(xml)} 바이트")


def test_arrow_shape_in_xml():
    """양방향 화살표 선 도형(cxnSp)이 XML에 포함되는지 확인"""
    xml = _export_and_read_drawing_xml(SAMPLE_SIGNAL)
    assert 'cxnSp' in xml, (
        "cxnSp(선 도형) 태그가 drawing XML에 없음\n"
        f"실제 XML (첫 500자):\n{xml[:500]}"
    )
    print("[PASS] cxnSp 선 도형 존재 확인")


def test_textbox_shape_in_xml():
    """텍스트 상자(txBody)가 XML에 포함되는지 확인"""
    xml = _export_and_read_drawing_xml(SAMPLE_SIGNAL)
    assert 'txBody' in xml, (
        "txBody(텍스트상자) 태그가 drawing XML에 없음\n"
        f"실제 XML (첫 500자):\n{xml[:500]}"
    )
    print("[PASS] txBody 텍스트상자 존재 확인")


def test_timing_label_text_in_xml():
    """실제 타이밍 라벨 텍스트(delay=10us → '10us')가 XML에 있는지 확인"""
    xml = _export_and_read_drawing_xml(SAMPLE_SIGNAL)
    assert '10us' in xml or '40us' in xml, (
        "타이밍 라벨 텍스트('10us' 또는 '40us')가 drawing XML에 없음\n"
        f"실제 XML:\n{xml}"
    )
    print("[PASS] 타이밍 라벨 텍스트 확인")


def test_dc_signal_no_shapes():
    """DC 신호(delay=width=period=0)는 도형이 생성되지 않아야 함"""
    dc_signal = {**SAMPLE_SIGNAL, 'delay': 0.0, 'width': 0.0, 'period': 0.0}
    exp = ExcelWaveformExporter()
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        path = f.name
    try:
        exp.export(path, [dc_signal], 1000.0, "DCModel")
        with zipfile.ZipFile(path, 'r') as z:
            drawing_files = [n for n in z.namelist() if 'drawing' in n and n.endswith('.xml')]
        # DC 신호만 있으면 도형이 없으므로 drawing 파일이 없어야 함
        assert not drawing_files, (
            f"DC 신호만 있는데 drawing 파일이 생성됨: {drawing_files}"
        )
        print("[PASS] DC 신호: 도형 없음 확인")
    finally:
        os.unlink(path)


def test_relationship_file_exists():
    """worksheet relationship 파일에 drawing 관계가 등록됐는지 확인"""
    exp = ExcelWaveformExporter()
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        path = f.name
    try:
        exp.export(path, [SAMPLE_SIGNAL], 1000.0, "TestModel")
        with zipfile.ZipFile(path, 'r') as z:
            names = z.namelist()
            rels_files = [n for n in names if '_rels' in n and 'sheet' in n]
            found_drawing_rel = False
            for rel_file in rels_files:
                content = z.read(rel_file).decode('utf-8')
                if 'drawing' in content.lower():
                    found_drawing_rel = True
                    break
        assert found_drawing_rel, (
            "worksheet .rels 파일에 drawing 관계가 없음!\n"
            f"검사한 rels 파일: {rels_files}\n"
            "→ openpyxl이 ws._drawing 을 save 시 인식하지 못함\n"
            "  해결: _apply_shapes_to_worksheets 방식 변경 필요"
        )
        print("[PASS] drawing 관계(.rels) 등록 확인")
    finally:
        os.unlink(path)


if __name__ == '__main__':
    tests = [
        test_drawing_file_exists,
        test_arrow_shape_in_xml,
        test_textbox_shape_in_xml,
        test_timing_label_text_in_xml,
        test_dc_signal_no_shapes,
        test_relationship_file_exists,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}:\n  {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n결과: {passed}개 통과 / {failed}개 실패")
    if failed:
        print("\n도형이 보이지 않는다면 test_relationship_file_exists 실패를 확인하세요.")
        print("→ _apply_shapes_to_worksheets 의 ws._drawing 설정이 openpyxl save와 연동 안 됨")
