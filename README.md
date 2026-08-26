# Final_Image_Metadata

이미지 메타데이터 추출 프로토타입 — `exiftool`로 메타데이터를 뽑아 민감/불필요 필드를 제거한 뒤 JSON으로 저장합니다.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![ExifTool](https://img.shields.io/badge/ExifTool-metadata-orange?style=flat-square)
![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square)

<br>

## 설치

```bash
sudo apt-get update
sudo apt-get install -y libimage-exiftool-perl
exiftool -ver
```

<br>

## Prototype 로직

**Real 판정 → 이미지 파일 경로 입력 → ExifTool 실행 → JSON 파싱 → 특정 키 제거 → JSON 파일 저장**

| 단계 | 내용 |
|:---:|:---|
| 1 | `extract_metadata_to_json_file(image_path, output_json_path, is_real=...)` 호출 |
| 2 | `is_real=False`(AI 판정)면 추출 없이 `None` 반환, 아니면 다음 단계로 진행 |
| 3 | 내부에서 `run_exiftool_json(image_path)` 실행 |
| 4 | `exiftool -json ... <image>` 실행 결과(stdout)를 JSON으로 파싱 |
| 5 | dict에서 `ExifToolVersion` / `Directory` / `FilePermissions` / `SourceFile` 제거 |
| 6 | 결과를 `output_json_path`에 JSON으로 저장 |
| 7 | (옵션) 저장한 dict를 리턴 → 추가 후처리/DB 저장 등에 사용 가능 |

<br>

## 사용법

```bash
python Proto_extract_metadata.py <이미지 경로> [-o <출력 JSON 경로>] [--exiftool-bin <exiftool 경로>] [--is-ai]
```

- `-o`를 생략하면 `<이미지 파일명>_metadata.json`으로 같은 폴더에 저장합니다.
- `--is-ai`는 업스트림에서 AI 생성물로 판정된 경우를 시뮬레이션 — 지정 시 추출 없이 종료합니다.
