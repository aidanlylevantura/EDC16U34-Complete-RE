/* EDC16U34 (MPC563) Custom OS Linker Script */
MEMORY
{
    flash (rx)  : ORIGIN = 0x00000000, LENGTH = 2M
    sram  (rwx) : ORIGIN = 0x003F8000, LENGTH = 32K
    immr  (rw)  : ORIGIN = 0x006FC000, LENGTH = 32K
}

SECTIONS
{
    .text : {
        *(.text.startup)
        *(.text)
        *(.rodata)
    } > flash

    .data : {
        *(.data)
    } > sram AT > flash

    .bss : {
        *(.bss)
    } > sram
}
