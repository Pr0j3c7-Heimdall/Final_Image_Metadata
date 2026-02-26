# Final_Image_Metadata
이미지 메타데이터 추출 코드 최종

<br>

## Linux 설치 방법
```
sudo apt-get update 
sudo apt-get install -y libimage-exiftool-perl 
exiftool -ver 
```

<br>

## Prototype 로직
**Real 판정 → 이미지 파일 경로 입력 → ExifTool 실행 → JSON 파싱 → 특정 키 제거 → JSON 파일 저장**
```
구체 단계:

1. extract_metadata_to_json_file(image_path, output_json_path) 호출
2. 내부에서 run_exiftool_json(image_path) 실행
3. exiftool -json ... <image> 실행 결과(stdout)를 JSON으로 파싱
4. dict에서 ExifToolVersion / Directory / FilePermissions / SourceFile 제거
5. 결과를 output_json_path에 JSON으로 저장
6. (옵션) 저장한 dict를 리턴 → 추가 후처리/DB 저장 등에 사용 가능
```

<br>

**비워 놓은 것(구현 해야하는 것)**
```
1. Real 판정 조건 연결(분기(Real/AI) 로직 붙이기)
2. 이미지 파일 경로 결정(이미지 입력 경로 하드코딩하는 걸로 만들어 놓고 비워놨어)
3. JSON 저장 경로/이름 규칙(json 출력 경로도 하드코딩 해놓고 비워놨음)
4. ExifTool 바이너리 위치/환경(지금은 같은 경로로 놔뒀는데 이것도 위치 정해서 해줘.)
5. 운영 예외 처리/보안(이건 안했는데 필요한지 판단해서 알잘딱해줘. timeout (exiftool이 비정상 파일에서 오래 걸릴 수 있데), stderr 경고 로그 저장, 파일 접근 권한/격리 (untrusted upload 처리) 등)
```

<br>

로직은 정상작동 됨.   
코드 고치고 Readme도 고쳐주라.   
대 종 범 화이팅!
