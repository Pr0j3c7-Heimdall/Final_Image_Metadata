import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Set


# ExifTool 결과에서 제거할 태그들
# - ExifTool Version Number  -> JSON에서는 보통 "ExifToolVersion"
# - Directory                -> "Directory"
# - File Permissions         -> "FilePermissions"
# - 경로 정보(SourceFile)     -> "SourceFile"
DEFAULT_EXCLUDE_TAGS: Set[str] = {
    "ExifToolVersion",
    "Directory",
    "FilePermissions",
    "SourceFile",  # ✅ 경로/원본 위치 정보 제거
}


def _base_tag(tag: str) -> str:
    """
    ExifTool은 옵션/상황에 따라 'File:Directory' 같은 "그룹:태그" 형태를 내보낼 수도 있음.
    이 함수는 ':' 뒤의 실제 태그명만 뽑아내서 필터링을 안정적으로 하기 위함.
    예) 'File:Directory' -> 'Directory'
    """
    return tag.split(":")[-1]


def run_exiftool_json(
    image_path: str | Path,
    *,
    exiftool_bin: str = "exiftool",
    extra_args: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """
    1) exiftool을 실행해서 JSON 출력(-json)을 받고
    2) JSON 배열 중 첫 번째(해당 파일의 메타데이터 dict)를 반환.

    반환 예:
    {
      "SourceFile": "/path/to/image.jpg",
      "ExifToolVersion": 13.51,
      "FileName": "image.jpg",
      ...
    }
    """
    image_path = Path(image_path)

    # exiftool 커맨드 구성
    cmd = [
        exiftool_bin,
        "-json",                  # JSON으로 출력
        "-struct",                # XMP 구조체/배열 형태 유지(깨지지 않게)
        "-charset", "filename=utf8",  # 한글 파일명(리눅스/윈도) 호환성 향상
        str(image_path),
    ]

    # 필요하면 추가 옵션을 끼워 넣을 수 있도록(예: -G1 등)
    if extra_args:
        cmd[1:1] = list(extra_args)

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    # exiftool 실패(파일 깨짐/권한/바이너리 문제 등)
    if proc.returncode != 0:
        raise RuntimeError(
            f"exiftool failed (exit={proc.returncode}). stderr:\n{proc.stderr.strip()}"
        )

    # exiftool은 1개 파일도 JSON 배열(list)로 반환하는 게 일반적
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Failed to parse exiftool JSON output: {e}\n"
            f"Raw stdout (first 2000 chars):\n{proc.stdout[:2000]}"
        )

    if not isinstance(payload, list) or not payload:
        raise RuntimeError(f"Unexpected exiftool JSON payload type/empty: {type(payload)}")

    if not isinstance(payload[0], dict):
        raise RuntimeError(f"Unexpected exiftool JSON item type: {type(payload[0])}")

    return payload[0]


def filter_metadata(
    meta: Dict[str, Any],
    *,
    exclude_tags: Optional[Set[str]] = None,
) -> Dict[str, Any]:
    """
    meta(dict)에서 exclude_tags에 해당하는 키를 제거해서 새 dict 반환.

    - 'Directory'처럼 일반 키도 제거
    - 'File:Directory'처럼 그룹 접두사가 붙은 키도 제거(안정성)
    """
    exclude_tags = exclude_tags or set(DEFAULT_EXCLUDE_TAGS)

    filtered: Dict[str, Any] = {}
    for k, v in meta.items():
        # 1) 키가 정확히 일치하는 경우 제거
        if k in exclude_tags:
            continue

        # 2) 그룹 접두사 제거 후 태그명이 제외 대상이면 제거
        if _base_tag(k) in exclude_tags:
            continue

        filtered[k] = v

    return filtered


def extract_metadata_to_json_file(
    image_path: str | Path,
    output_json_path: str | Path,
    *,
    exiftool_bin: str = "exiftool",
    exclude_tags: Optional[Set[str]] = None,
    pretty: bool = True,
) -> Dict[str, Any]:
    """
    ✅ 메인 로직 함수 (프레임워크에서 Real 판정 후 호출하면 됨)

    1) image_path로 exiftool 실행해서 메타데이터 dict 획득
    2) (ExifToolVersion, Directory, FilePermissions, SourceFile) 등 제외
    3) 결과를 output_json_path에 저장
    4) filtered dict를 반환(추가 처리에 사용 가능)
    """
    # 1) 추출
    meta = run_exiftool_json(image_path, exiftool_bin=exiftool_bin)

    # 2) 필터링
    filtered = filter_metadata(meta, exclude_tags=exclude_tags)

    # 3) 저장 경로 준비
    output_json_path = Path(output_json_path)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)

    # 4) JSON 저장
    with output_json_path.open("w", encoding="utf-8") as f:
        if pretty:
            json.dump(filtered, f, ensure_ascii=False, indent=2)
        else:
            json.dump(filtered, f, ensure_ascii=False)

    return filtered


# --- Example usage (backend friend가 이 부분을 프레임워크에 연결) ---
if __name__ == "__main__":
    img = ""
    out = ""

    extract_metadata_to_json_file(
        img,
        out,
        exiftool_bin="exiftool",  # 또는 "/usr/bin/exiftool"
        pretty=True,
    )
