% =========================================================
% MathTool Hexadecimal and Binary Integer Literal Example
% =========================================================
% Demonstrates MATLAB-style:
%
% - Hexadecimal literals: 0x... and 0X...
% - Binary literals:      0b... and 0B...
% - Integer suffixes:     u8/u16/u32/u64 and s8/s16/s32/s64
% - Two's-complement signed interpretation
% - Conversion helpers:   dec2hex, dec2bin, hex2dec, bin2dec
% - Bitwise helpers:      bitand, bitor, bitxor, bitshift, bitget, bitset
% =========================================================

disp("Hexadecimal and binary integer literal example");

% ---------------------------------------------------------
% Basic literals
% ---------------------------------------------------------

HEX_LOWER = 0x2A;
HEX_UPPER = 0X2A;

BIN_LOWER = 0b101010;
BIN_UPPER = 0B101010;

disp("Basic literals all represent decimal 42:");
disp([HEX_LOWER HEX_UPPER BIN_LOWER BIN_UPPER]);


% ---------------------------------------------------------
% Arithmetic with integer literals
% ---------------------------------------------------------

ARITHMETIC_RESULT = 0x10 + 0b10;

fprintf("0x10 + 0b10 = %d\n", ARITHMETIC_RESULT);


% ---------------------------------------------------------
% Matrix literals
% ---------------------------------------------------------

INTEGER_MATRIX = [
    0x1  0x2;
    0b11 0b100
];

disp("Matrix created from hex and binary literals:");
disp(INTEGER_MATRIX);


% ---------------------------------------------------------
% Typed unsigned and signed integer suffixes
% ---------------------------------------------------------

UINT8_VALUE = 0xFFu8;
UINT16_VALUE = 0b101010u16;

INT8_POSITIVE = 0x2As8;
INT8_NEGATIVE = 0xFFs8;
INT16_NEGATIVE = 0xFFFFs16;

disp("Typed integer examples:");
fprintf("0xFFu8 class: %s, value: %d\n", class(UINT8_VALUE), UINT8_VALUE);
fprintf("0b101010u16 class: %s, value: %d\n", class(UINT16_VALUE), UINT16_VALUE);
fprintf("0x2As8 class: %s, value: %d\n", class(INT8_POSITIVE), INT8_POSITIVE);
fprintf("0xFFs8 class: %s, value: %d\n", class(INT8_NEGATIVE), INT8_NEGATIVE);
fprintf("0xFFFFs16 class: %s, value: %d\n", class(INT16_NEGATIVE), INT16_NEGATIVE);


% ---------------------------------------------------------
% Conversion helpers
% ---------------------------------------------------------

HEX_TEXT = dec2hex(255);
BIN_TEXT = dec2bin(16);

HEX_NUMBER = hex2dec("FF");
BIN_NUMBER = bin2dec("1010");

disp("Conversion helper results:");
disp(HEX_TEXT);
disp(BIN_TEXT);
disp(HEX_NUMBER);
disp(BIN_NUMBER);


% ---------------------------------------------------------
% Bitwise helpers
% ---------------------------------------------------------

REGISTER = 0b10010110u8;

MASKED_BIT = bitand(REGISTER, 0b00010000u8);
FIFTH_BIT = bitshift(MASKED_BIT, -4);

REGISTER_CLEARED = bitset(REGISTER, 5, false);
REGISTER_WITH_LOW_BIT = bitset(REGISTER_CLEARED, 1, true);

AND_RESULT = bitand(0b1100, 0b1010);
OR_RESULT = bitor(0b1100, 0b1010);
XOR_RESULT = bitxor(0b1100, 0b1010);
SHIFT_LEFT_RESULT = bitshift(0b0011, 2);
SHIFT_RIGHT_RESULT = bitshift(0b1100, -2);
SECOND_BIT = bitget(0b1010, 2);

disp("Bitwise helper results:");
fprintf("REGISTER = %s\n", dec2bin(REGISTER));
fprintf("Fifth bit = %d\n", FIFTH_BIT);
fprintf("After clearing bit 5 = %s\n", dec2bin(REGISTER_CLEARED));
fprintf("After setting bit 1 = %s\n", dec2bin(REGISTER_WITH_LOW_BIT));
fprintf("bitand(0b1100, 0b1010) = %d\n", AND_RESULT);
fprintf("bitor(0b1100, 0b1010) = %d\n", OR_RESULT);
fprintf("bitxor(0b1100, 0b1010) = %d\n", XOR_RESULT);
fprintf("bitshift(0b0011, 2) = %d\n", SHIFT_LEFT_RESULT);
fprintf("bitshift(0b1100, -2) = %d\n", SHIFT_RIGHT_RESULT);
fprintf("bitget(0b1010, 2) = %d\n", SECOND_BIT);


% ---------------------------------------------------------
% Expected values for quick workspace inspection
% ---------------------------------------------------------

EXPECTED_BASIC = [42 42 42 42];
EXPECTED_MATRIX = [1 2; 3 4];
EXPECTED_ARITHMETIC_RESULT = 18;
EXPECTED_INT8_NEGATIVE = -1;
EXPECTED_INT16_NEGATIVE = -1;
EXPECTED_HEX_TEXT = "FF";
EXPECTED_BIN_TEXT = "10000";

disp("Example complete");
