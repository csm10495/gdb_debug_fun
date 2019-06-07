#include <stdint.h>

typedef struct _version
{
    uint16_t versionMajor;
    uint16_t versionMinor;
} version;

typedef union _u
{
    uint16_t asInt;
    char asChars[2];
} our_union;

typedef struct b
{
    version version;
    our_union u;
    uint32_t id;
    uint8_t tokens[8];
    uint8_t bit1 : 1;
    uint8_t bit23 : 2;
    uint8_t bitOther : 5;
} Bs_t;

Bs_t b;

int main()
{
    return 0;
}