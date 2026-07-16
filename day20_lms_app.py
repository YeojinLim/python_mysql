# < pymysql 라이브러리를 사용한 학생 출결관리 시스템 >

import pymysql

try:
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="class1234",
        database="lms",
        charset="utf8"
    )

    cursor = conn.cursor()

    while True:

        # 영문자는 대문자로 변경
        student_id = input("학생 아이디(q/Q 종료) : ").upper()
        
        # exit 장치
        if student_id == "Q":
            break

        # 학생 존재 여부 확인
        sql = """
        SELECT *
        FROM student
        WHERE id=%s
        """

        cursor.execute(sql, (student_id,)) 
        # pymysql은 값 전달 시 반드시 '묶음(튜플/리스트)' 형태를 요구함
        # 원소가 1개인 튜플을 만들기 위해 끝에 쉼표(,)를 꼭 붙여줌 (안 붙이면 에러)

        # 1. 학생 여부 확인
        # 조회 결과가 없으면(NULL이면) 반환값은 None, 있으면 튜플(tuple) 하나를 반환한다.
        if cursor.fetchone() is None:
            print("존재하지 않는 학생입니다.")
            continue

        
        # 2. 입력한 학생의 오늘 출석 정보 조회
        # 없으면 None, 있다면 퇴실 여부 확인을 위해 "leave_time"값만 조회
        sql = """
        SELECT leave_time
        FROM attendance
        WHERE id=%s AND attend_date=CURDATE()
        """

        cursor.execute(sql, (student_id,))
        result = cursor.fetchone()

        # ------------------------------------------------------------
        # result 결과셋이 없으면 --> 입실처리
        # leave_time컬럼 값이 있지만 값이 null 이면 --> 퇴실처리
        # leave_time컬럼 값이 있고 퇴실 시간이 나온다면 --> 퇴실완료상태
        # 3가지로 분기
        # ------------------------------------------------------------

        # (1) 오늘날짜의 출결정보가 없으면 출석(입실) -> INSERT
        if result is None:

            sql = """
            INSERT INTO attendance(id, attend_date, enter_time, leave_time)
            VALUES(%s, CURDATE(), CURTIME(), NULL)
            """

            cursor.execute(sql, (student_id,))
            conn.commit() # 저장

            print("입실 처리 완료")

        # (2) SELECT절의 첫번째[0] 조회 열(leave_time)값이 NULL이면 -> 퇴실하지 않은 경우 -> 퇴실시간 NULL에서 수정 -> UPDATE
        elif result[0] is None:

            sql = """
            UPDATE attendance
            SET leave_time=CURTIME()
            WHERE id=%s
              AND attend_date=CURDATE()
              AND leave_time IS NULL
            """

            cursor.execute(sql, (student_id,))
            conn.commit() 

            if cursor.rowcount == 1: # cursor.rowcount : 명령어로 인해 영향을 받은(추가, 수정, 삭제된) 행(Row)의 개수를 알려줌
                print("퇴실 처리 완료")
            else:
                print("퇴실 처리 실패")

        # (3) 오늘 날짜의 학생정보도 있고, 퇴실시간도 NULL이 아니면 ->  퇴실한 경우
        else:
            print("이미 퇴실 처리된 학생입니다.")

# 에러 발생시
except Exception as e:
    print("프로그램 오류 :", e)

# 마지막에 항상 실행
finally:
    cursor.close()
    conn.close()
    print("프로그램 종료")    