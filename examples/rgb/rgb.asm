; 'rgb.png' (78 bytes)
; MD5:    16ea7bf3d2646deffc7a4e6677ba77d0
; SHA1:   72c726c643d9cb4f883d519203be9d831a4dedc0
; SHA256: 39f28e794c8c011947341f23fb4b3c4d3c7744886579c4f86276f9b4df946177

; directives ===================================================================

[map symbols symbols.map]

; definitions ==================================================================

%macro ddbe 1
  db (%1>>8*3) & 0ffh
  db (%1>>8*2) & 0ffh
  db (%1>>8*1) & 0ffh
  db (%1>>8*0) & 0ffh
%endmacro

; code =========================================================================

db `\x89PNG\r\n\x1a\n`                            ; signature                    ;0000: 89 50 ..... 1a 0a (+8)

chunk1:                                           ; chunk1 { //Image Header
 ddbe 13                                          ;  length                      ;0008: 00 00 00 0d (+4)
;ddbe (chunk1.crc32 - chunk1.data)

.type db `IHDR`                                   ;  type                        ;000c: 49 48 44 52 (+4)

.data:                                            ; Data {
  incbin 'rgb.png', 0x10, 0xd                                                    ;0010: 00 00 ..... 00 00 (+13)
  ;}                                              ;   } //Data

.crc32 ddbe 0x948283e3                            ;  crc-32                      ;001d: 94 82 83 e3 (+4)
 ;> chunk1.crc32=CRC32(chunk1.type,chunk1.crc32)
;}                                                ; } //chunk

chunk2:                                           ; chunk2 { //Image Data
 ddbe 21                                          ;  length                      ;0021: 00 00 00 15 (+4)
;ddbe (chunk2.crc32 - chunk2.data)

.type db `IDAT`                                   ;  type                        ;0025: 49 44 41 54 (+4)

.data:                                            ; Data {
  incbin 'rgb.png', 0x29, 0x15                                                   ;0029: 08 1d ..... 02 fe (+21)
  ;}                                              ;   } //Data

.crc32 ddbe 0xe93261e5                            ;  crc-32                      ;003e: e9 32 61 e5 (+4)
 ;> chunk2.crc32=CRC32(chunk2.type,chunk2.crc32)
;}                                                ; } //chunk

chunk3:                                           ; chunk3 { //Image End
 ddbe 0                                           ;  length                      ;0042: 00 00 00 00 (+4)
;ddbe (chunk3.crc32 - chunk3.data)

.type db `IEND`                                   ;  type                        ;0046: 49 45 4e 44 (+4)

.data:
.crc32 ddbe 0xae426082                            ;  crc-32                      ;004a: ae 42 60 82 (+4)
 ;> chunk3.crc32=CRC32(chunk3.type,chunk3.crc32)
;}                                                ; } //chunk

