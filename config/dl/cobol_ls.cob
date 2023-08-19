       >>SOURCE FORMAT FREE

       IDENTIFICATION DIVISION.
       PROGRAM-ID. DL.

       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 PTR POINTER.
       01 ENV-NAME PIC XXX VALUE "BIN".
       01 ENV-LEN PIC 9(8) BINARY.

       01 REPO PIC X(37) VALUE "eclipse-che4z/che-che4z-lsp-for-cobol".
       01 B-1 PIC X(19) VALUE "https://github.com/".
       01 B-2 PIC X(26) VALUE "/releases/latest/download/".
       01 B-3 PIC X(22) VALUE "cobol-language-support".
       01 BASE PIC X(104).

       LINKAGE SECTION.
       01 ENV PIC X(9999).

       PROCEDURE DIVISION.
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
