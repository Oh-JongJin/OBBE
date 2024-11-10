import os
import glob


def convert_class_numbers(directory_path='.'):
    """
    현재 디렉토리의 모든 txt 파일에서 클래스 번호 0을 10으로 변경합니다.
    
    Args:
        directory_path (str): 처리할 텍스트 파일이 있는 디렉토리 경로
    """
    # txt 파일 목록 가져오기
    txt_files = glob.glob(os.path.join(directory_path, '*.txt'))
    
    if not txt_files:
        print("현재 디렉토리에 텍스트 파일이 없습니다.")
        return
    
    modified_count = 0
    
    for txt_file in txt_files:
        modified = False
        new_lines = []
        
        # 파일 읽기
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 각 줄 처리
        for line in lines:
            parts = line.strip().split()
            if parts and parts[0] == '0':  # 첫 번째 숫자(클래스)가 0인 경우
                parts[0] = '10'  # 0을 10으로 변경
                modified = True
            new_lines.append(' '.join(parts) + '\n')
        
        # 변경된 내용이 있는 경우에만 파일 쓰기
        if modified:
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            modified_count += 1
            print(f"수정됨: {txt_file}")
    
    print(f"\n처리 완료!")
    print(f"총 {len(txt_files)}개의 파일 중 {modified_count}개 파일이 수정되었습니다.")

if __name__ == "__main__":
    convert_class_numbers()