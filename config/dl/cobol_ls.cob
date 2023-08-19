       >>SOURCE FORMAT FREE

       IDENTIFICATION DIVISION.
       PROGRAM-ID. DL.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
       SELECT TMPF ASSIGN TO "owo.txt".

       DATA DIVISION.
       FILE SECTION.
       FD TMPF.
       01 TMP PIC X(9999).

       WORKING-STORAGE SECTION.
       01 OSTYPE PIC 9(38).

       01 PTR POINTER.
       01 ENV-NAME PIC XXX VALUE "BIN".
       01 ENV-LEN PIC 9(8) BINARY.
       01 RETVAL PIC 999 VALUE 0.

       01 REPO PIC X(37) VALUE "eclipse-che4z/che-che4z-lsp-for-cobol".
       01 B-1 PIC X(19) VALUE "https://github.com/".
       01 B-2 PIC X(26) VALUE "/releases/latest/download/".
       01 B-3 PIC X(22) VALUE "cobol-language-support".
       01 BASE PIC X(104).

       01 BASHOS PIC X(33) VALUE "bash -c 'printf -- %s\n $OSTYPE' >".
       01 BEX PIC X(34) VALUE "bash -Eeuo pipefail -O failglob -c".

       LINKAGE SECTION.
       01 ENV PIC X(9999).

       PROCEDURE DIVISION.
           CALL "SYSTEM" USING BASHOS RETURNING RETVAL.

           IF RETVAL NOT = 0
             MOVE RETVAL TO RETURN-CODE
             EXIT PROGRAM
           END-IF.

           OPEN INPUT TMPF.
           READ TMPF into TMP.
           CLOSE TMPF.
           DISPLAY TMP.

           STRING B-1 REPO B-2 B-3 DELIMITED SIZE INTO BASE.
           DISPLAY BASE.

           SET PTR TO ADDRESS OF ENV-NAME.
           CALL "getenv" USING BY VALUE PTR RETURNING PTR
           IF PTR = NULL THEN
             MOVE 1 TO RETURN-CODE
             EXIT PROGRAM
           ELSE
             SET ADDRESS OF ENV TO PTR
             MOVE 0 TO ENV-LEN
             INSPECT ENV TALLYING ENV-LEN
               FOR CHARACTERS BEFORE INITIAL X"00"
             DISPLAY ENV(1:ENV-LEN)
           END-IF.


        *> CALL "SYSTEM" USING CMD RETURNING RETVAL.
        *> DISPLAY RETURN-CODE.

        *> IF RETVAL NOT = 0
        *>        MOVE RETVAL TO RETURN-CODE
        *>        EXIT PROGRAM
        *> ELSE
        *>        DISPLAY "NOPE"
        *> END-IF.
