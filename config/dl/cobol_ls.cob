       >>SOURCE FORMAT FREE

       IDENTIFICATION DIVISION.
       PROGRAM-ID. DL.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
       SELECT TMPF ASSIGN TO "tmp.txt".

       DATA DIVISION.
       FILE SECTION.
       FD TMPF.
       01 TMP PIC X(9999).

       WORKING-STORAGE SECTION.
       01 PTR POINTER.
       01 ENV-NAME PIC XXX VALUE "BIN".
       01 ENV-LEN PIC 9(8) BINARY.

       01 BIN PIC X(99).
       01 TMPD PIC X(99).

       01 SH PIC X(999).
       01 SPIT PIC X(8) VALUE ">tmp.txt".
       01 RETVAL PIC 999 VALUE 0.

       01 OSTYPE PIC X(99).
       01 OS-IDX PIC 99.

       01 REPO PIC X(37) VALUE "eclipse-che4z/che-che4z-lsp-for-cobol".
       01 VERSION PIC X(99).
       01 URI PIC X(999).

       LINKAGE SECTION.
       01 ENV PIC X(9999).

       PROCEDURE DIVISION.
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
             MOVE ENV(1:ENV-LEN) TO BIN
           END-IF.

           MOVE SPACES TO SH.
           MOVE SPACES TO TMP.

           STRING "mktemp -d" " " SPIT DELIMITED SIZE INTO SH.
           CALL "SYSTEM" USING SH RETURNING RETVAL.
           IF RETVAL NOT = 0
             MOVE RETVAL TO RETURN-CODE
             EXIT PROGRAM
           END-IF.
           OPEN INPUT TMPF.
           READ TMPF into TMPD.
           CLOSE TMPF.

           MOVE SPACES TO SH.
           MOVE SPACES TO TMP.

           STRING "bash -c 'printf -- %s $OSTYPE'"
           " " SPIT DELIMITED SIZE INTO SH.
           CALL "SYSTEM" USING SH RETURNING RETVAL.
           IF RETVAL NOT = 0
             MOVE RETVAL TO RETURN-CODE
             EXIT PROGRAM
           END-IF.
           OPEN INPUT TMPF.
           READ TMPF into OSTYPE.
           CLOSE TMPF.

           MOVE SPACES TO SH.
           MOVE SPACES TO TMP.

           STRING "gh-latest.sh" " " REPO " " SPIT
           DELIMITED SIZE INTO SH.
           CALL "SYSTEM" USING SH RETURNING RETVAL.
           IF RETVAL NOT = 0
             MOVE RETVAL TO RETURN-CODE
             EXIT PROGRAM
           END-IF.
           OPEN INPUT TMPF.
           READ TMPF into VERSION.
           CLOSE TMPF.

           STRING "https://github.com/" REPO
           "/releases/latest/download/cobol-language-support"
           DELIMITED SIZE INTO URI.

           MOVE 0 TO OS-IDX.
           INSPECT OSTYPE TALLYING OS-IDX FOR LEADING "linux".
           IF OS-IDX = 1
             STRING URI "-linux-x64-" VERSION ".vsix"
             DELIMITED BY " " INTO URI
           END-IF.

           MOVE 0 TO OS-IDX.
           INSPECT OSTYPE TALLYING OS-IDX FOR LEADING "darwin".
           IF OS-IDX = 1
             STRING URI "-darwin-arm64-" VERSION ".vsix"
             DELIMITED BY " " INTO URI
           END-IF.

           MOVE 0 TO OS-IDX.
           INSPECT OSTYPE TALLYING OS-IDX FOR LEADING "msys".
           IF OS-IDX = 1
             STRING BIN ".exe" DELIMITED BY SIZE INTO BIN
             STRING URI "-win32-x64-" VERSION "-signed.vsix"
             DELIMITED BY " " INTO URI
           END-IF.

           DISPLAY TMPD.
           DISPLAY URI.
