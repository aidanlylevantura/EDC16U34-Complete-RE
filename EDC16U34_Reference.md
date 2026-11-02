# VW Golf 5 EDC16U34 KH Master Reference

**VW Golf 5 1.9 TDI PD 105 hp — EDC16U34 — 03G906021KH / 0281013226 / 380437**

Generated: 2026-10-31 21:57

---

## Platform

| Field | Value |
|---|---|
| ECU | Bosch EDC16U34 |
| Vehicle | VW Golf 5 1.9 TDI PD 105 hp (2006) |
| VAG part no | 03G906021KH |
| Bosch part no | 0281013226 |
| Software version | 380437 |
| CPU | PowerPC MPC563 |
| Flash dump size | 2 MB (0x000000–0x1FFFFF) |
| IMMR base | 0x006FC000 |

## Resolved RE Facts

| Fact | Address / Value |
|---|---|
| Seed LFSR polynomial table | `0x2240` (64 × 32-bit) |
| Seed handler (UDS 0x27) | `DSM_FUN_000017a4 @ 0x17A4` |
| FADECAFE self-check region | `0x4D284–0x52804` |
| Boot verify signature walker | `DSM_auto_00486c @ 0x486C` |
| Warm-start SPRG1 magic | `0x1A` |
| Cruise stalk decoder | `CrCtl_FUN_000db0a0 @ 0xDB0A0` |
| **VIN** | **WVWZZZ1KZ6W165917** (EEPROM @ 0x0145, 0x0165) |
| **IMMO/FIN** | **VWZBZ0F0361686** (EEPROM @ 0x00EC, 0x010C, 0x012C) |
| **Login / PIN** | **4441 (0x1159)** (EEPROM @ 0x00E8) |

## Function Inventory

- Total functions: **2366**
- Named (meaningful): **2366**
- Unnamed (FUN_/func_): **0**

## Calibration Maps

**10834 maps total.**

| Address | Name | Dimensions |
|---|---|---|
| `0x001C203C` | `ACCCD_aDesLimNeg_CUR` | 0x6308 |
| `0x001C2052` | `ACCCD_aDesLimPos_CUR` | 0x48F4 |
| `0x001C205C` | `ACCCD_aDesNegOffset_C` | 0x-1 |
| `0x001C205E` | `ACCCD_aDesPosOffset_C` | 0x-1 |
| `0x001C2060` | `ACCCD_tiaDesDebDef_C` | 0x-1 |
| `0x001C2062` | `ACCCD_tiaDesDebOk_C` | 0x-1 |
| `0x001C1DD8` | `ACCCD_aGvtyGnd_C` | 0x-1 |
| `0x001C1DDA` | `ACCCD_aLongPhiCor_C` | 0x-1 |
| `0x001C1DAC` | `ACCCD_tiBrkErrDebDef_C` | 0x-1 |
| `0x001C1DAE` | `ACCCD_tiBrkErrDebOk_C` | 0x-1 |
| `0x001C1DB0` | `ACCCD_tiBrkNPLDebDef_C` | 0x-1 |
| `0x001C1DB2` | `ACCCD_tiBrkNPLDebOk_C` | 0x-1 |
| `0x001C1DEC` | `ACCCD_facATrnvrs_CUR` | 0x0 |
| `0x001C1E42` | `ACCCD_facCosPhi_CUR` | 0x33F3 |
| `0x001C1E88` | `ACCCD_facCwVal_C` | 0x-1 |
| `0x001C1EA6` | `ACCCD_facEnv_MAP` | 0x-1 |
| `0x001C2080` | `ACCCD_facKiCorr_MAP` | 0x-1 |
| `0x001C20E4` | `ACCCD_facKpCorr_MAP` | 0x-1 |
| `0x001C1F36` | `ACCCD_facSinPhi_CUR` | 0x3D2A |
| `0x001C1F8A` | `ACCCD_frStrtFrc_CUR` | 0x20 |
| `0x001C213A` | `ACCCD_IKiBrk_CUR` | 0x20 |
| `0x001C2166` | `ACCCD_IKiPos_MAP` | 0x-1 |
| `0x001C21C6` | `ACCCD_lWhlRds_C` | 0x-1 |
| `0x001C21C8` | `ACCCD_mRtnlCor_C` | 0x-1 |
| `0x001C21CA` | `ACCCD_mRtnlWhl_C` | 0x-1 |
| `0x001C21CC` | `ACCCD_mRtnl_C` | 0x-1 |
| `0x001C1F96` | `ACCCD_mVehRef_C` | 0x-1 |
| `0x001C1F98` | `ACCCD_mVehTare_C` | 0x-1 |
| `0x001C1F9A` | `ACCCD_mVehTrail_C` | 0x-1 |
| `0x001D4AB8` | `ACCCD_tiTrqDesPT1_C` | 0x-1 |
| `0x001C1FE4` | `ACCCD_phiArcSin_CUR` | 0xC409 |
| `0x001C21DC` | `ACCCD_PKpBrk_CUR` | 0x0 |
| `0x001C2208` | `ACCCD_PKpPos_MAP` | 0x-1 |
| `0x001C227C` | `ACCCD_dtrqSlpPos_C` | 0x-1 |
| `0x001C2280` | `ACCCD_dtrqSlpNeg_C` | 0x-1 |
| `0x001C2268` | `ACCCD_rAxleRed_C` | 0x-1 |
| `0x001C1DB4` | `ACCCD_tiSensErrDebDef_C` | 0x-1 |
| `0x001C1DB6` | `ACCCD_tiSensErrDebOk_C` | 0x-1 |
| `0x001C0A1A` | `ACCCD_stACCnew_Vector` | 0x-1 |
| `0x001C0A1B` | `ACCCD_stACCnew_Channel` | 0x-1 |
| `0x001C0A1C` | `ACCCD_stACC_Vector` | 0x-1 |
| `0x001C0A1D` | `ACCCD_stACC_Channel` | 0x-1 |
| `0x001C1DB8` | `ACCCD_stBrk1ErrMsk_C` | 0x-1 |
| `0x001C1DB9` | `ACCCD_stBrk8ErrMsk_C` | 0x-1 |
| `0x001C1DBA` | `ACCCD_stBrkErrMsk_C` | 0x-1 |
| `0x001C226A` | `ACCCD_stBrkMsk_C` | 0x-1 |
| `0x001C1DBB` | `ACCCD_stBrkNav_C` | 0x-1 |
| `0x001C1DBC` | `ACCCD_stBrkNotAvMsk_C` | 0x-1 |
| `0x001C1DBD` | `ACCCD_stBrkNPLMsk_C` | 0x-1 |
| `0x001C0A1E` | `ACCCD_stBrk_Vector` | 0x-1 |
| `0x001C0A1F` | `ACCCD_stBrk_Channel` | 0x-1 |
| `0x001C1DBE` | `ACCCD_stCANErrMsk_C` | 0x-1 |
| `0x001C1DBF` | `ACCCD_stDrvBrkMsk_C` | 0x-1 |
| `0x001C1DC0` | `ACCCD_tiEPBOn_C` | 0x-1 |
| `0x001C1DC2` | `ACCCD_tiEPBShOff_C` | 0x-1 |
| `0x001C1DC4` | `ACCCD_swtActBrk_C` | 0x-1 |
| `0x001C1DC5` | `ACCCD_swtBrkType_C` | 0x-1 |
| `0x001C226B` | `ACCCD_swtCtrlOff_C` | 0x-1 |
| `0x001C226C` | `ACCCD_swtDragLimEna_C` | 0x-1 |
| `0x001C226D` | `ACCCD_swtECDa_C` | 0x-1 |
| `0x001C226E` | `ACCCD_swtGvnrOutI_C` | 0x-1 |
| `0x001C202A` | `ACCCD_swtVehMassAdpt_C` | 0x-1 |
| `0x001C1DC6` | `ACCCD_tiBrkTrqDet_C` | 0x-1 |
| `0x001C202C` | `ACCCD_tiPhiPT1_C` | 0x-1 |
| `0x001C1DC8` | `ACCCD_tiSwtOffRmp_C` | 0x-1 |
| `0x001C1DCC` | `ACCCD_trqBrkDetUp_C` | 0x-1 |
| `0x001C1DD0` | `ACCCD_trqBrkDetDwn_C` | 0x-1 |
| `0x001C2284` | `ACCCD_trqBrkMax_C` | 0x-1 |
| `0x001C2288` | `ACCCD_trqBrkMin_C` | 0x-1 |
| `0x001C228C` | `ACCCD_trqBrkThres_C` | 0x-1 |
| `0x001C228E` | `ACCCD_trqBrkZero_C` | 0x-1 |
| `0x001C2270` | `ACCCD_trqCtrlLimMax_C` | 0x-1 |
| `0x001C2274` | `ACCCD_trqCtrlLimMin_C` | 0x-1 |
| `0x001C0A20` | `ACCCD_trqDesRaw_Vector` | 0x-1 |
| `0x001C0A21` | `ACCCD_trqDesRaw_Channel` | 0x-1 |
| `0x001C2278` | `ACCCD_trqDragOffSet_C` | 0x-1 |
| `0x001C2290` | `ACCCD_trqFrcDelta_C` | 0x-1 |
| `0x001C2292` | `ACCCD_trqFrcHyst_C` | 0x-1 |
| `0x001C1DD4` | `ACCCD_tiWrongCodedDebDef_C` | 0x-1 |
| `0x001C1DD6` | `ACCCD_tiWrongCodedDebOk_C` | 0x-1 |
| `0x001C2294` | `ACCD_tiDebCanSigDef_C` | 0x-1 |
| `0x001C2296` | `ACCD_tiDebCanSigOk_C` | 0x-1 |
| `0x001C2298` | `ACCD_ctPwrStgOnMax_C` | 0x-1 |
| `0x001C229A` | `ACCD_DebNoLoadDef_C` | 0x-1 |
| `0x001C229C` | `ACCD_DebNoLoadOk_C` | 0x-1 |
| `0x001C229E` | `ACCD_DebNoTempDef_C` | 0x-1 |
| `0x001C22A0` | `ACCD_DebNoTempOk_C` | 0x-1 |
| `0x001C22A2` | `ACCD_DebShortCircBatDef_C` | 0x-1 |
| `0x001C22A4` | `ACCD_DebShortCircBatOk_C` | 0x-1 |
| `0x001C22A6` | `ACCD_DebShortCircGndDef_C` | 0x-1 |
| `0x001C22A8` | `ACCD_DebShortCircGndOk_C` | 0x-1 |
| `0x001C22AA` | `ACCD_tiMnSwtDebNeg_C` | 0x-1 |
| `0x001C22AC` | `ACCD_tiMnSwtDebPos_C` | 0x-1 |
| `0x001C22AE` | `ACCD_tiDebPACMaxDef_C` | 0x-1 |
| `0x001C22B0` | `ACCD_tiDebPACMaxOk_C` | 0x-1 |
| `0x001C22B2` | `ACCD_tiDebPACMinDef_C` | 0x-1 |
| `0x001C22B4` | `ACCD_tiDebPACMinOk_C` | 0x-1 |
| `0x001C22B6` | `ACCD_tiDebPACSigDef_C` | 0x-1 |
| `0x001C22B8` | `ACCD_tiDebPACSigOk_C` | 0x-1 |
| `0x001C22BC` | `ACCD_tiRmpLo2Hi_C` | 0x-1 |
| `0x001C22C0` | `ACCD_tiRmpHi2Lo_C` | 0x-1 |
| `0x001C22C4` | `ACCD_stSensIDWord_C` | 0x-1 |
| `0x001C22C6` | `ACCD_pDfl_C` | 0x-1 |
| `0x001C22C8` | `ACCD_stPwmInInv_C` | 0x-1 |
| `0x001C22CA` | `ACCD_tiPwmInMinPer_C` | 0x-1 |
| `0x001C22CC` | `ACCD_tiPwmInMaxPer_C` | 0x-1 |
| `0x001C22CE` | `ACCD_dcycPwmInMin_C` | 0x-1 |
| `0x001C22D0` | `ACCD_dcycPwmInMax_C` | 0x-1 |
| `0x001C22D8` | `ACCD_rLin_CUR` | 0x1027 |
| `0x001C22DC` | `ACCD_stACDfl_C` | 0x-1 |
| `0x001C22DE` | `ACCD_stComprDigIn_C` | 0x-1 |
| `0x001C22DF` | `ACCD_stInvOut_C` | 0x-1 |
| `0x001C22E0` | `ACCD_stMnSwtInvIn_C` | 0x-1 |
| `0x001C22E1` | `ACCD_stSPICtl_C` | 0x-1 |
| `0x001C22E2` | `ACCD_swtACtypeVal_C` | 0x-1 |
| `0x001C22E3` | `ACCD_swtACtypeType_C` | 0x-1 |
| `0x001C22E4` | `ACCD_swtClimatronic_C` | 0x-1 |
| `0x001C22E5` | `ACCD_swtComprON_C` | 0x-1 |
| `0x001C22E6` | `ACCD_tiBtwTst_C` | 0x-1 |
| `0x001C22E8` | `ACCD_tiComprON_C` | 0x-1 |
| `0x001C22EA` | `ACCD_tiPwrStgOn_C` | 0x-1 |
| `0x001C22EC` | `ACCD_trqComprDfl_C` | 0x-1 |
| `0x001C22EE` | `ACCD_trqComprHi_C` | 0x-1 |
| `0x001C22F0` | `ACCD_trqComprLo_C` | 0x-1 |
| `0x001C22F4` | `AccPed_tiDebAliveDef_C` | 0x-1 |
| `0x001C22F6` | `AccPed_tiDebAliveOk_C` | 0x-1 |
| `0x001C22F8` | `AccPed_tiDebPladrLckDef_C` | 0x-1 |
| `0x001C22FA` | `AccPed_tiDebPladrLckOk_C` | 0x-1 |
| `0x001C22FC` | `AccPed_tiDebMisUseOk_C` | 0x-1 |
| `0x001C22FE` | `AccPed_tiDebMisUseDef_C` | 0x-1 |
| `0x001C2300` | `AccPed_dfacRampSlope_C` | 0x-1 |
| `0x001C2304` | `AccPed_drAPPUnFltLim_C` | 0x-1 |
| `0x001C2306` | `AccPed_drLimpMax_C` | 0x-1 |
| `0x001C2308` | `AccPed_drLimUp_C` | 0x-1 |
| `0x001C230C` | `AccPed_drLimDwn_C` | 0x-1 |
| `0x001C2310` | `AccPed_nErr_C` | 0x-1 |
| `0x001C2312` | `AccPed_nLIMinBrk_C` | 0x-1 |
| `0x001C2314` | `AccPed_nLIMinvHigh_C` | 0x-1 |
| `0x001C2316` | `AccPed_nLIMinvLow_C` | 0x-1 |
| `0x001C2318` | `AccPed_nLimMisUse_C` | 0x-1 |
| `0x001C231A` | `AccPed_nLimNMR_C` | 0x-1 |
| `0x001C231C` | `AccPed_nLim_C` | 0x-1 |
| `0x001C231E` | `AccPed_nPlaAPPBrk_C` | 0x-1 |
| `0x001C2320` | `AccPed_tiPlausBrkDebNeg_C` | 0x-1 |
| `0x001C2322` | `AccPed_tiPlausBrkDebPos_C` | 0x-1 |
| `0x001C0A26` | `AccPed_rChkdVal_Vector` | 0x-1 |
| `0x001C0A27` | `AccPed_rChkdVal_Channel` | 0x-1 |
| `0x001C2324` | `AccPed_rErrValPlaus_C` | 0x-1 |
| `0x001C2326` | `AccPed_rLimpMax_C` | 0x-1 |
| `0x001C2328` | `AccPed_rPlaMaxVal_C` | 0x-1 |
| `0x001C232A` | `AccPed_rThPlaus_C` | 0x-1 |
| `0x001C232C` | `AccPed_rThresPrpMin_C` | 0x-1 |
| `0x001C232E` | `AccPed_rThresPrp_C` | 0x-1 |
| `0x001C2330` | `AccPed_rThresSfty_C` | 0x-1 |
| `0x001C2332` | `AccPed_rZero_C` | 0x-1 |
| `0x001C2334` | `AccPed_stBrkPlausMSK_C` | 0x-1 |
| `0x001C2344` | `AccPed_stGearSel_CUR` | 0xFF |
| `0x001C2354` | `AccPed_swtAliveDetEna_C` | 0x-1 |
| `0x001C2355` | `AccPed_swtAppGradEna_C` | 0x-1 |
| `0x001C2356` | `AccPed_swtBrkDet_C` | 0x-1 |
| `0x001C2357` | `AccPed_swtEPBEna_C` | 0x-1 |
| `0x001C2358` | `AccPed_swtMisUseEna_C` | 0x-1 |
| `0x001C2359` | `AccPed_swtPlausCheckReqd_C` | 0x-1 |
| `0x001C235A` | `AccPed_swtrVnFltEna_C` | 0x-1 |
| `0x001C235B` | `AccPed_swtrVnFreeze_C` | 0x-1 |
| `0x001C235C` | `AccPed_swtTipSlitIsSport_C` | 0x-1 |
| `0x001C235D` | `AccPed_swtTrqRampEna_C` | 0x-1 |
| `0x001C235E` | `AccPed_swtTrqTransType_C` | 0x-1 |
| `0x001C235F` | `AccPed_swtVehDynReqd_C` | 0x-1 |
| `0x001C2360` | `AccPed_tiChkDebNeg_C` | 0x-1 |
| `0x001C2362` | `AccPed_tiChkDebPos_C` | 0x-1 |
| `0x001C2364` | `AccPed_tiDebPlaDet_C` | 0x-1 |
| `0x001C2366` | `AccPed_tiDebPlaRst_C` | 0x-1 |
| `0x001C2368` | `AccPed_tiPlaAPPBrkCANwaitHW_C` | 0x-1 |
| `0x001C236C` | `AccPed_tiVnTrqEngPT1_C` | 0x-1 |
| `0x001C0A22` | `AccPed_trqDes_Vector` | 0x-1 |
| `0x001C0A23` | `AccPed_trqDes_Channel` | 0x-1 |
| `0x001C23A4` | `AccPed_trqEng0_MAP` | 0x-1 |
| `0x001C24FA` | `AccPed_trqEng1_MAP` | 0x-1 |
| `0x001C2650` | `AccPed_trqEng2_MAP` | 0x-1 |
| `0x001C27A6` | `AccPed_trqEng3_MAP` | 0x-1 |
| `0x001C28FC` | `AccPed_trqEng4_MAP` | 0x-1 |
| `0x001C2A52` | `AccPed_trqEng5_MAP` | 0x-1 |
| `0x001C2BA8` | `AccPed_trqEng6_MAP` | 0x-1 |
| `0x001C2CFE` | `AccPed_trqEngLow_MAP` | 0x-1 |
| `0x001C0A24` | `AccPed_trqLead_Vector` | 0x-1 |
| `0x001C0A25` | `AccPed_trqLead_Channel` | 0x-1 |
| `0x001C2E20` | `AccPed_trqNMRMax_C` | 0x-1 |
| `0x001C2E50` | `AccPed_trqPrpSport_MAP` | 0x-1 |
| `0x001C2F3C` | `AccPed_trqPrp_MAP` | 0x-1 |
| `0x001C2FFC` | `AccPed_vLim_C` | 0x-1 |
| `0x001C3000` | `AccPed_vThresLI_C` | 0x-1 |
| `0x001C3004` | `ACCtl_drAccPedHi_C` | 0x-1 |
| `0x001C3006` | `ACCtl_drAccPedLo_C` | 0x-1 |
| `0x001C3008` | `ACCtl_nAccVehHi_C` | 0x-1 |
| `0x001C300A` | `ACCtl_nAccVehLo_C` | 0x-1 |
| `0x001C300C` | `ACCtl_nDAEngHi_C` | 0x-1 |
| `0x001C300E` | `ACCtl_nDAEngLo_C` | 0x-1 |
| `0x001C30E8` | `ACCtl_nKliIdlSpd_C` | 0x-1 |
| `0x001C3010` | `ACCtl_nLIGovHi_C` | 0x-1 |
| `0x001C3012` | `ACCtl_nLIGovLo_C` | 0x-1 |
| `0x001C3014` | `ACCtl_nLIGovRelHi_C` | 0x-1 |
| `0x001C3016` | `ACCtl_nLIGovRelLo_C` | 0x-1 |
| `0x001C3018` | `ACCtl_nSysErrHi_C` | 0x-1 |
| `0x001C301A` | `ACCtl_nSysErrLo_C` | 0x-1 |
| `0x001C301C` | `ACCtl_pAccValHi_C` | 0x-1 |
| `0x001C301E` | `ACCtl_pAccValLo_C` | 0x-1 |
| `0x001C3020` | `ACCtl_pACPMaxHi_C` | 0x-1 |
| `0x001C3022` | `ACCtl_pACPMaxLo_C` | 0x-1 |
| `0x001C3024` | `ACCtl_pACPMinHi_C` | 0x-1 |
| `0x001C3026` | `ACCtl_pACPMinLo_C` | 0x-1 |
| `0x001C3028` | `ACCtl_rAccPedHi_C` | 0x-1 |
| `0x001C302A` | `ACCtl_rAccPedLo_C` | 0x-1 |
| `0x001C302C` | `ACCtl_stDAGearHi_C` | 0x-1 |
| `0x001C302D` | `ACCtl_stDAGearLo_C` | 0x-1 |
| `0x001C30EA` | `ACCtl_swtEnableRequest_C` | 0x-1 |
| `0x001C302E` | `ACCtl_swtFanErrEna_C` | 0x-1 |
| `0x001C302F` | `ACCtl_swtnLIGovRelEna_C` | 0x-1 |
| `0x001C30EC` | `ACCtl_swtoff_mode_C` | 0x-1 |
| `0x001C3030` | `ACCtl_swtTempACOff_C` | 0x-1 |
| `0x001C3031` | `ACCtl_swtTempHys_C` | 0x-1 |
| `0x001C30EE` | `ACCtl_swtVehStand_C` | 0x-1 |
| `0x001C3032` | `ACCtl_tAccAir1Hi_C` | 0x-1 |
| `0x001C3034` | `ACCtl_tAccAir1Lo_C` | 0x-1 |
| `0x001C3036` | `ACCtl_tAccAir2Hi_C` | 0x-1 |
| `0x001C3038` | `ACCtl_tAccAir2Lo_C` | 0x-1 |
| `0x001C303A` | `ACCtl_tACPairHi_C` | 0x-1 |
| `0x001C303C` | `ACCtl_tACPairLo_C` | 0x-1 |
| `0x001C303E` | `ACCtl_tiAccAirMin_C` | 0x-1 |
| `0x001C3040` | `ACCtl_tiAccMin_C` | 0x-1 |
| `0x001C3042` | `ACCtl_tiACOnDly_C` | 0x-1 |
| `0x001C3044` | `ACCtl_tiACPmin_C` | 0x-1 |
| `0x001C3050` | `ACCtl_tiACStrtDly_CUR` | 0x2003 |
| `0x001C3058` | `ACCtl_tiCANESCU_C` | 0x-1 |
| `0x001C305A` | `ACCtl_tiCANGearbx_C` | 0x-1 |
| `0x001C3070` | `ACCtl_tiDAmax_MAP` | 0x-1 |
| `0x001C30A4` | `ACCtl_tiDAmin_MAP` | 0x-1 |
| `0x001C30C4` | `ACCtl_tiLIGov_C` | 0x-1 |
| `0x001C30F0` | `ACCtl_tiMaxTSCfreezeReduction_C` | 0x-1 |
| `0x001C30F2` | `ACCtl_tiMaxTSCfreeze_C` | 0x-1 |
| `0x001C30F4` | `ACCtl_tiMinSwitchOn_C` | 0x-1 |
| `0x001C30F6` | `ACCtl_tiMinSwitchReduction_C` | 0x-1 |
| `0x001C30C6` | `ACCtl_tiSysErrmin_C` | 0x-1 |
| `0x001C30C8` | `ACCtl_tiTempRedMin_C` | 0x-1 |
| `0x001C30CA` | `ACCtl_tiWTmin_C` | 0x-1 |
| `0x001C30CC` | `ACCtl_tTempRedHi_C` | 0x-1 |
| `0x001C30CE` | `ACCtl_tTempRedLo_C` | 0x-1 |
| `0x001C30D8` | `ACCtl_tWTHi_CUR` | 0x7D10 |
| `0x001C30DE` | `ACCtl_tWTSubthresh_C` | 0x-1 |
| `0x001C30E0` | `ACCtl_vAccVehHi_C` | 0x-1 |
| `0x001C30E2` | `ACCtl_vAccVehLo_C` | 0x-1 |
| `0x001C30E4` | `ACCtl_vDAVehHi_C` | 0x-1 |
| `0x001C30E6` | `ACCtl_vDAVehLo_C` | 0x-1 |
| `0x001C1D20` | `ACC_aDevCnclOvr_C` | 0x-1 |
| `0x001C1D22` | `ACC_daThresNeg_C` | 0x-1 |
| `0x001C1D24` | `ACC_daThresPos_C` | 0x-1 |
| `0x001C1D26` | `ACC_tiDebStEPBInAct_C` | 0x-1 |
| `0x001C1D28` | `ACC_tiDebStEPBAct_C` | 0x-1 |
| `0x001C1D2A` | `ACC_tiDebSwtPlInAct_C` | 0x-1 |
| `0x001C1D2C` | `ACC_tiDebSwtPlAct_C` | 0x-1 |
| `0x001C1D30` | `ACC_dtrqBrkEngSlp_C` | 0x-1 |
| `0x001C1D3A` | `ACC_dtrqBrkRmpDwn_CUR` | 0x0 |
| `0x001C1D44` | `ACC_dtrqBrkRmpUp_CUR` | 0xB80B |
| `0x001C1D48` | `ACC_dtrqBrkUpSlpMin_C` | 0x-1 |
| `0x001C1D4C` | `ACC_dtrqEngDwnSlpMin_C` | 0x-1 |
| `0x001C1D50` | `ACC_dtrqNoOverride_C` | 0x-1 |
| `0x001C1D54` | `ACC_dtrqOverride_C` | 0x-1 |
| `0x001C1D58` | `ACC_factrqMin_C` | 0x-1 |
| `0x001C1D5A` | `ACC_nShutOffMin_C` | 0x-1 |
| `0x001C1D68` | `ACC_rBrk_CUR` | 0xF401 |
| `0x001C1D7E` | `ACC_rPedThres_C` | 0x-1 |
| `0x001C0A10` | `ACC_stCrCtl_Vector` | 0x-1 |
| `0x001C0A11` | `ACC_stCrCtl_Channel` | 0x-1 |
| `0x001C0A12` | `ACC_stDrvBrk_Vector` | 0x-1 |
| `0x001C0A13` | `ACC_stDrvBrk_Channel` | 0x-1 |
| `0x001C0A14` | `ACC_stOvrRun_Vector` | 0x-1 |
| `0x001C0A15` | `ACC_stOvrRun_Channel` | 0x-1 |
| `0x001C1D80` | `ACC_swtACCCnclOvr_C` | 0x-1 |
| `0x001C1D81` | `ACC_swtDrvBrkCond_C` | 0x-1 |
| `0x001C1D82` | `ACC_swtNoEngFault_C` | 0x-1 |
| `0x001C1D84` | `ACC_tiACCCnclOvrDly_C` | 0x-1 |
| `0x001C1D86` | `ACC_tiBattShutOff_C` | 0x-1 |
| `0x001C1D88` | `ACC_tiBrkDrvCut_C` | 0x-1 |
| `0x001C1D8A` | `ACC_tiBrkDrvDef_C` | 0x-1 |
| `0x001C1D8C` | `ACC_tiDebBrkAct_C` | 0x-1 |
| `0x001C1D8E` | `ACC_tiDebLockOffAct_C` | 0x-1 |
| `0x001C1D90` | `ACC_tiDelayClth_C` | 0x-1 |
| `0x001C1D92` | `ACC_tiStrtDlyPlausChk_C` | 0x-1 |
| `0x001C1D94` | `ACC_trqDesMax_C` | 0x-1 |
| `0x001C1D98` | `ACC_trqDesOffset_C` | 0x-1 |
| `0x001C0A16` | `ACC_trqDes_Vector` | 0x-1 |
| `0x001C0A17` | `ACC_trqDes_Channel` | 0x-1 |
| `0x001C0A18` | `ACC_trqLead_Vector` | 0x-1 |
| `0x001C0A19` | `ACC_trqLead_Channel` | 0x-1 |
| `0x001C1D9C` | `ACC_trqNoOvr2_C` | 0x-1 |
| `0x001C1DA0` | `ACC_dtrqRmpSlpUp_C` | 0x-1 |
| `0x001C1DA4` | `ACC_dtrqRmpSlpDwn_C` | 0x-1 |
| `0x001C1DA8` | `ACC_uBattShutOff_C` | 0x-1 |
| `0x001C30F8` | `ACTrqC_tiDT1TrqDyn_C` | 0x-1 |
| `0x001C30FC` | `ACTrqC_dDT1TrqDynfact_C` | 0x-1 |
| `0x001C3100` | `ACTrqC_factDiv_C` | 0x-1 |
| `0x001C3102` | `ACTrqC_factMul_C` | 0x-1 |
| `0x001C3104` | `ACTrqC_swtCalc_C` | 0x-1 |
| `0x001C3105` | `ACTrqC_swtCANtrq_C` | 0x-1 |
| `0x001C312A` | `ACTrqC_trqConvp_MAP` | 0x-1 |
| `0x001C31BE` | `ACTrqC_trqConvt_MAP` | 0x-1 |
| `0x001C1D18` | `AC_pwrAdjValDef_C` | 0x-1 |
| `0x001C1D1A` | `AC_pwrAdjValMax_C` | 0x-1 |
| `0x001C1D1C` | `AC_pwrAdjValMin_C` | 0x-1 |
| `0x001C1D1E` | `AC_rTrans_C` | 0x-1 |
| `0x001C1CA6` | `ADCMon_DebQueueDef_C` | 0x-1 |
| `0x001C1CA8` | `ADCMon_DebRefVltgSRCDef_C` | 0x-1 |
| `0x001C1CAA` | `ADCMon_DebTstImpDef_C` | 0x-1 |
| `0x001C1CAC` | `ADCMon_nQueueMon_C` | 0x-1 |
| `0x001C1CB0` | `ADCMon_tiQueueMon_C` | 0x-1 |
| `0x001C1CB2` | `ADCMon_tiSendTstImp_C` | 0x-1 |
| `0x001C1CB4` | `ADCMon_uRefSRCMax_C` | 0x-1 |
| `0x001C1CB6` | `ADCMon_uRefSRCMin_C` | 0x-1 |
| `0x001C1CB8` | `ADCMon_uTstImpSRCMax_C` | 0x-1 |
| `0x001C0FA8` | `Signals_adFreeApplic1_C` | 0x-1 |
| `0x001C0FAC` | `Signals_numTypFreeApplic1_C` | 0x-1 |
| `0x001C0FB0` | `Signals_adFreeApplic2_C` | 0x-1 |
| `0x001C0FB4` | `Signals_numTypFreeApplic2_C` | 0x-1 |
| `0x001C0FB8` | `Signals_adFreeApplic3_C` | 0x-1 |
| `0x001C0FBC` | `Signals_numTypFreeApplic3_C` | 0x-1 |
| `0x001C0FC0` | `Signals_adFreeApplic4_C` | 0x-1 |
| `0x001C0FC4` | `Signals_numTypFreeApplic4_C` | 0x-1 |
| `0x001C3250` | `AFSCD_dmAirThrSRCLo_C` | 0x-1 |
| `0x001C3252` | `AFSCD_dmAirThrSRCHi_C` | 0x-1 |
| `0x001C3296` | `AFSCD_dmLin_CUR` | 0x581B |
| `0x001C32D6` | `AFSCD_facSwtOnCor_C` | 0x-1 |
| `0x001C32D8` | `AFSCD_tiSwtOnCor_C` | 0x-1 |
| `0x001C32DA` | `AFSCD_DebPlHiOffsDrftDef_C` | 0x-1 |
| `0x001C32DC` | `AFSCD_DebPlHiOffsDrftOk_C` | 0x-1 |
| `0x001C32DE` | `AFSCD_DebPlHiSetyDrftDef_C` | 0x-1 |
| `0x001C32E0` | `AFSCD_DebPlHiSetyDrftOk_C` | 0x-1 |
| `0x001C32E2` | `AFSCD_DebPlLoOffsDrftDef_C` | 0x-1 |
| `0x001C32E4` | `AFSCD_DebPlLoOffsDrftOk_C` | 0x-1 |
| `0x001C32E6` | `AFSCD_DebPlLoSetyDrftDef_C` | 0x-1 |
| `0x001C32E8` | `AFSCD_DebPlLoSetyDrftOk_C` | 0x-1 |
| `0x001C32EA` | `AFSCD_DebSRCHiAirmDef_C` | 0x-1 |
| `0x001C32EC` | `AFSCD_DebSRCHiAirmOk_C` | 0x-1 |
| `0x001C32EE` | `AFSCD_DebSRCHiSplyVltgDef_C` | 0x-1 |
| `0x001C32F0` | `AFSCD_DebSRCHiSplyVltgOk_C` | 0x-1 |
| `0x001C32F2` | `AFSCD_DebSRCLoAirmDef_C` | 0x-1 |
| `0x001C32F4` | `AFSCD_DebSRCLoAirmOk_C` | 0x-1 |
| `0x001C32F6` | `AFSCD_DebSRCLoSplyVltgDef_C` | 0x-1 |
| `0x001C32F8` | `AFSCD_DebSRCLoSplyVltgOk_C` | 0x-1 |
| `0x001C32FA` | `AFSCD_dmAirPerTimeDfl_C` | 0x-1 |
| `0x001C0A2C` | `AFSCD_dmAirPerTime_Vector` | 0x-1 |
| `0x001C0A2D` | `AFSCD_dmAirPerTime_Channel` | 0x-1 |
| `0x001C3330` | `AFSCD_dmCorrAirPerTime2_CUR` | 0xF401 |
| `0x001C33A0` | `AFSCD_dmCorrAirPerTime_CUR` | 0xC012 |
| `0x001C3434` | `AFSCD_dmPlsCor_MAP` | 0x-1 |
| `0x001C3640` | `AFSCD_facAirPerCylCor_MAP` | 0x-1 |
| `0x001C3708` | `AFSCD_facCorrVal_MAP` | 0x-1 |
| `0x001C383C` | `AFSCD_facPlsCor_MAP` | 0x-1 |
| `0x001C3A60` | `AFSCD_mAirPerCylDfl_MAP` | 0x-1 |
| `0x001C0A28` | `AFSCD_mAirPerCylPlsCor_Vector` | 0x-1 |
| `0x001C0A29` | `AFSCD_mAirPerCylPlsCor_Channel` | 0x-1 |
| `0x001C0A2A` | `AFSCD_mAirPerCyl_Vector` | 0x-1 |
| `0x001C0A2B` | `AFSCD_mAirPerCyl_Channel` | 0x-1 |
| `0x001C3B24` | `AFSCD_mPlsCor_MAP` | 0x-1 |
| `0x001C3D24` | `AFSCD_uThrHiPlOffsDrft_C` | 0x-1 |
| `0x001C3D26` | `AFSCD_uThrLoPlOffsDrft_C` | 0x-1 |
| `0x001C3D28` | `AFSCD_tClntThrLoShtrp_C` | 0x-1 |
| `0x001C3D2A` | `AFSCD_pAirThrLoShtrp_C` | 0x-1 |
| `0x001C3D2C` | `AFSCD_qRawThrHiShtrp_C` | 0x-1 |
| `0x001C3D2E` | `AFSCD_nAvrgThrLoPlHiShtrp_C` | 0x-1 |
| `0x001C3D30` | `AFSCD_nAvrgThrHiPlHiShtrp_C` | 0x-1 |
| `0x001C3D32` | `AFSCD_rAirThrHiPlHiShtrp_C` | 0x-1 |
| `0x001C3D34` | `AFSCD_nAvrgThrLoPlLoShtrp_C` | 0x-1 |
| `0x001C3D36` | `AFSCD_nAvrgThrHiPlLoShtrp_C` | 0x-1 |
| `0x001C3D38` | `AFSCD_rAirThrLoPlLoShtrp_C` | 0x-1 |
| `0x001C3D3C` | `AFSCD_tClntThrLo_C` | 0x-1 |
| `0x001C3D3E` | `AFSCD_tClntThrHi_C` | 0x-1 |
| `0x001C3D40` | `AFSCD_rSwirlThrHi_C` | 0x-1 |
| `0x001C3D42` | `AFSCD_pAirThrLo_C` | 0x-1 |
| `0x001C3D44` | `AFSCD_qRawThrHi_C` | 0x-1 |
| `0x001C3D46` | `AFSCD_nAvrgThrLoPlHi_C` | 0x-1 |
| `0x001C3D48` | `AFSCD_nAvrgThrHiPlHi_C` | 0x-1 |
| `0x001C3D4A` | `AFSCD_pBstThrHiPlHi_C` | 0x-1 |
| `0x001C3D4C` | `AFSCD_rAirThrHiPlHi_C` | 0x-1 |
| `0x001C3D4E` | `AFSCD_nAvrgThrLoPlLo_C` | 0x-1 |
| `0x001C3D50` | `AFSCD_nAvrgThrHiPlLo_C` | 0x-1 |
| `0x001C3D52` | `AFSCD_pBstThrLoPlLo_C` | 0x-1 |
| `0x001C3D54` | `AFSCD_rAirThrLoPlLo_C` | 0x-1 |
| `0x001C3D56` | `AFSCD_rEGRPThrHi_C` | 0x-1 |
| `0x001C3D58` | `AFSCD_rTVAPThrHi_C` | 0x-1 |
| `0x001C3D5C` | `AFSCD_tiDlyEGRPPlSetyDrft_C` | 0x-1 |
| `0x001C3D60` | `AFSCD_tiDlyStrPlSetyDrft_C` | 0x-1 |
| `0x001C3D64` | `AFSCD_pNormAir_C` | 0x-1 |
| `0x001C3D68` | `AFSCD_tiPT1rAirNorm_C` | 0x-1 |
| `0x001C0B28` | `AFSCD_tiLPFilt_C` | 0x-1 |
| `0x001C3D86` | `AFSCD_qAirmThrSRCHiActv_CUR` | 0x9F17 |
| `0x001C3D9E` | `AFSCD_nAvrgThrLoSRCLo_C` | 0x-1 |
| `0x001C3DA0` | `AFSCD_nAvrgThrHiSRCLo_C` | 0x-1 |
| `0x001C3DA2` | `AFSCD_tiDlyActvSRCHiAirm_C` | 0x-1 |
| `0x001C3E10` | `AFSCD_swtAirSysVal_C` | 0x-1 |
| `0x001C3E11` | `AFSCD_swtAirSysType_C` | 0x-1 |
| `0x001C3DA4` | `AFSCD_swtDebCfg_C` | 0x-1 |
| `0x001C3DA5` | `AFSCD_swtSwtOnCor_C` | 0x-1 |
| `0x001C3DC6` | `AFSCD_tAirTempCorr_CUR` | 0x0 |
| `0x001C3E0C` | `AFSCD_tiOffsDrftTstLim_C` | 0x-1 |
| `0x001C3E0E` | `AFSCD_tNormAir_C` | 0x-1 |
| `0x001C9F7C` | `BasAdj_AFVCDnSetpoint_C` | 0x-1 |
| `0x001C9F7E` | `BasAdj_AFVCDtime_C` | 0x-1 |
| `0x001C9F80` | `BasAdj_AFVCDBits_C` | 0x-1 |
| `0x001C3E12` | `AFVCD_ctPwrStgOnMax_C` | 0x-1 |
| `0x001C3E14` | `AFVCD_DebExcTempDef_C` | 0x-1 |
| `0x001C3E16` | `AFVCD_DebExcTempOk_C` | 0x-1 |
| `0x001C3E18` | `AFVCD_DebNoLdDef_C` | 0x-1 |
| `0x001C3E1A` | `AFVCD_DebNoLdOk_C` | 0x-1 |
| `0x001C3E1C` | `AFVCD_DebShCirBattDef_C` | 0x-1 |
| `0x001C3E1E` | `AFVCD_DebShCirBattOk_C` | 0x-1 |
| `0x001C3E20` | `AFVCD_DebShCirGndDef_C` | 0x-1 |
| `0x001C3E22` | `AFVCD_DebShCirGndOk_C` | 0x-1 |
| `0x001C3E24` | `AFVCD_stActrInvOut_C` | 0x-1 |
| `0x001C3E25` | `AFVCD_stPwrStgActrActv_C` | 0x-1 |
| `0x001C3E26` | `AFVCD_stPwrStgActrDia_C` | 0x-1 |
| `0x001C3E27` | `AFVCD_stSPICtl_C` | 0x-1 |
| `0x001C3E28` | `AFVCD_tiBtwTst_C` | 0x-1 |
| `0x001C3E2A` | `AFVCD_tiPwrStgOn_C` | 0x-1 |
| `0x001C3E2C` | `AFVCtl_dmAcouHighOff_C` | 0x-1 |
| `0x001C3E2E` | `AFVCtl_dmAcouHighOn_C` | 0x-1 |
| `0x001C3E30` | `AFVCtl_dmAcouLowOff_C` | 0x-1 |
| `0x001C3E32` | `AFVCtl_dmAcouLowOn_C` | 0x-1 |
| `0x001C3E34` | `AFVCtl_dmHeightOff_C` | 0x-1 |
| `0x001C3E36` | `AFVCtl_dmHeightOn_C` | 0x-1 |
| `0x001C3E38` | `AFVCtl_dmPwrOff_C` | 0x-1 |
| `0x001C3E3A` | `AFVCtl_dmPwrOn_C` | 0x-1 |
| `0x001C3E3C` | `AFVCtl_dmRainHighOff_C` | 0x-1 |
| `0x001C3E3E` | `AFVCtl_dmRainHighOn_C` | 0x-1 |
| `0x001C3E40` | `AFVCtl_dmRainLowOff_C` | 0x-1 |
| `0x001C3E42` | `AFVCtl_dmRainLowOn_C` | 0x-1 |
| `0x001C3E44` | `AFVCtl_dmSnowHighOff_C` | 0x-1 |
| `0x001C3E46` | `AFVCtl_dmSnowHighOn_C` | 0x-1 |
| `0x001C3E48` | `AFVCtl_dmSnowLowOff_C` | 0x-1 |
| `0x001C3E4A` | `AFVCtl_dmSnowLowOn_C` | 0x-1 |
| `0x001C3E4C` | `AFVCtl_nAcouHighOff_C` | 0x-1 |
| `0x001C3E4E` | `AFVCtl_nAcouHighOn_C` | 0x-1 |
| `0x001C3E50` | `AFVCtl_nAcouLowOff_C` | 0x-1 |
| `0x001C3E52` | `AFVCtl_nAcouLowOn_C` | 0x-1 |
| `0x001C3E54` | `AFVCtl_pHeightOff_C` | 0x-1 |
| `0x001C3E56` | `AFVCtl_pHeightOn_C` | 0x-1 |
| `0x001C3E58` | `AFVCtl_tiRainWiperHoldNeg_C` | 0x-1 |
| `0x001C3E5A` | `AFVCtl_tiRainWiperHoldPos_C` | 0x-1 |
| `0x001C3E5C` | `AFVCtl_tAirSnowOff_C` | 0x-1 |
| `0x001C3E5E` | `AFVCtl_tAirSnowOn_C` | 0x-1 |
| `0x001C3E60` | `AFVCtl_tIndPwrOff_C` | 0x-1 |
| `0x001C3E62` | `AFVCtl_tIndPwrOn_C` | 0x-1 |
| `0x001C3E64` | `AFVCtl_tIndSnowOff_C` | 0x-1 |
| `0x001C3E66` | `AFVCtl_tIndSnowOn_C` | 0x-1 |
| `0x001C3E68` | `AFVCtl_vRainHighOff_C` | 0x-1 |
| `0x001C3E6A` | `AFVCtl_vRainHighOn_C` | 0x-1 |
| `0x001C3E6C` | `AFVCtl_vRainLowOff_C` | 0x-1 |
| `0x001C3E6E` | `AFVCtl_vRainLowOn_C` | 0x-1 |
| `0x001C3E70` | `AFVCtl_vSnowHighOff_C` | 0x-1 |
| `0x001C3E72` | `AFVCtl_vSnowHighOn_C` | 0x-1 |
| `0x001C3E74` | `AFVCtl_vSnowLowOff_C` | 0x-1 |
| `0x001C3E76` | `AFVCtl_vSnowLowOn_C` | 0x-1 |
| `0x001C3E78` | `AirbCD_DebCrashCrCtlDef_C` | 0x-1 |
| `0x001C3E7A` | `AirbCD_DebCrashCrCtlOk_C` | 0x-1 |
| `0x001C3E7C` | `AirbCD_DebCrashPSPDef_C` | 0x-1 |
| `0x001C3E7E` | `AirbCD_DebCrashPSPOk_C` | 0x-1 |
| `0x001C3E80` | `AirbCD_DebCrashDef_C` | 0x-1 |
| `0x001C3E82` | `AirbCD_DebCrashOk_C` | 0x-1 |
| `0x001C3E84` | `AirbCD_stAIRBCrCtl_C` | 0x-1 |
| `0x001C3E85` | `AirbCD_stAIRBFuel_C` | 0x-1 |
| `0x001C4A8E` | `AirCtl_APCorRgn_CUR` | 0x0 |
| `0x001C4AA0` | `AirCtl_APCor_CUR` | 0x0 |
| `0x001C4AB4` | `AirCtl_ATCorRgn_MAP` | 0x-1 |
| `0x001C4ACC` | `AirCtl_ATCor_MAP` | 0x-1 |
| `0x001C4B00` | `AirCtl_CTCorRgn_CUR` | 0x20 |
| `0x001C4B16` | `AirCtl_CTCor_CUR` | 0x0 |
| `0x001C3E88` | `AirCtl_dqDesThr_C` | 0x-1 |
| `0x001C3E8A` | `AirCtl_drBPAThr_C` | 0x-1 |
| `0x001C4B20` | `AirCtl_drOvrRunAtcpHi_C` | 0x-1 |
| `0x001C4B22` | `AirCtl_drOvrRunAtcpLo_C` | 0x-1 |
| `0x001C4B24` | `AirCtl_DT1CoNeg_C` | 0x-1 |
| `0x001C56D0` | `AirCtl_DT1_C` | 0x-1 |
| `0x001C56D4` | `AirCtl_DKd_C` | 0x-1 |
| `0x001C56D8` | `AirCtl_DKdPos_C` | 0x-1 |
| `0x001C56DC` | `AirCtl_DKdNeg_C` | 0x-1 |
| `0x001C56E0` | `AirCtl_dqDWinPos_C` | 0x-1 |
| `0x001C56E2` | `AirCtl_dqDWinNeg_C` | 0x-1 |
| `0x001C4B28` | `AirCtl_DT1WmNeg_C` | 0x-1 |
| `0x001C6674` | `AirCtl_dtrqSmkLim_C` | 0x-1 |
| `0x001C4B2C` | `AirCtl_DT1CoPos_C` | 0x-1 |
| `0x001C4B30` | `AirCtl_DKdCo_C` | 0x-1 |
| `0x001C4B34` | `AirCtl_DKdPosCo_C` | 0x-1 |
| `0x001C4B38` | `AirCtl_DKdNegCo_C` | 0x-1 |
| `0x001C4B3C` | `AirCtl_dqDWinPosCo_C` | 0x-1 |
| `0x001C4B3E` | `AirCtl_dqDWinNegCo_C` | 0x-1 |
| `0x001C4B40` | `AirCtl_DT1WmPos_C` | 0x-1 |
| `0x001C4B44` | `AirCtl_DKdWm_C` | 0x-1 |
| `0x001C4B48` | `AirCtl_DKdPosWm_C` | 0x-1 |
| `0x001C4B4C` | `AirCtl_DKdNegWm_C` | 0x-1 |
| `0x001C4B50` | `AirCtl_dqDWinPosWm_C` | 0x-1 |
| `0x001C4B52` | `AirCtl_dqDWinNegWm_C` | 0x-1 |

## Crypto: LFSR Poly Table

**64 32-bit polynomials** at flash address **`0x2240`**.

| Index | Poly |
|---:|---|
| 0 | `0x0001C200` |
| 1 | `0x0A221289` |
| 2 | `0x144890A1` |
| 3 | `0x24212491` |
| 4 | `0x290A0285` |
| 5 | `0x42145091` |
| 6 | `0x504822C1` |
| 7 | `0x0A24C4C1` |
| 8 | `0x14252229` |
| 9 | `0x24250525` |
| 10 | `0x2510A491` |
| 11 | `0x28488863` |
| 12 | `0x29148885` |
| 13 | `0x422184A5` |
| 14 | `0x49128521` |
| 15 | `0x50844A85` |
| 16 | `0x620CC211` |
| 17 | `0x124452A9` |
| 18 | `0x18932251` |
| 19 | `0x2424A459` |
| 20 | `0x29149521` |
| 21 | `0x42352621` |
| 22 | `0x4A512289` |
| 23 | `0x52A48911` |
| 24 | `0x11891475` |
| 25 | `0x22346523` |
| 26 | `0x4A3118D1` |
| 27 | `0x64497111` |
| 28 | `0x0AE34529` |
| 29 | `0x15398989` |
| 30 | `0x22324A67` |
| 31 | `0x2D12B489` |
| 32 | `0x132A4A75` |
| 33 | `0x19B13469` |
| 34 | `0x25D2C453` |
| 35 | `0x4949349B` |
| 36 | `0x524E9259` |
| 37 | `0x1964CA6B` |
| 38 | `0x24F5249B` |
| 39 | `0x28979175` |
| 40 | `0x352A5959` |
| 41 | `0x3A391749` |
| 42 | `0x51D44EA9` |
| 43 | `0x564A4F25` |
| 44 | `0x6AD52649` |
| 45 | `0x76493925` |
| 46 | `0x25DE52C9` |
| 47 | `0x332E9333` |
| 48 | `0x68D64997` |
| 49 | `0x494947FB` |
| 50 | `0x33749ACF` |
| 51 | `0x5AD55B5D` |
| 52 | `0x7F272A4F` |
| 53 | `0x35BD5B75` |
| 54 | `0x3F5AD55D` |
| 55 | `0x5B5B6DAD` |
| 56 | `0x6B5DAD6B` |
| 57 | `0x75B57AD5` |
| 58 | `0x5DBAD56F` |
| 59 | `0x6DBF6AAD` |
| 60 | `0x75775EB5` |
| 61 | `0x5AEDFED5` |
| 62 | `0x6B5F7DD5` |
| 63 | `0x6F757B6B` |

## Crypto: FADECAFE Branches

**20 branch sites** in `FUN_0004d714`.

| # | Address | Op | Kind | Target |
|---:|---|---|---|---|
| 1 | `0x0004D75C` | `beq` | conditional | `0x0004D780` |
| 2 | `0x0004D798` | `beq` | conditional | `0x0004D7C4` |
| 3 | `0x0004D7DC` | `beq` | conditional | `0x0004D808` |
| 4 | `0x0004D820` | `beq` | conditional | `0x0004D84C` |
| 5 | `0x0004D864` | `beq` | conditional | `0x0004D890` |
| 6 | `0x0004D8B0` | `bne` | conditional | `0x0004D8C8` |
| 7 | `0x0004D8C4` | `beq` | conditional | `0x0004D8F0` |
| 8 | `0x0004D910` | `bgt` | conditional | `0x0004D918` |
| 9 | `0x0004D92C` | `bne` | conditional | `0x0004D938` |
| 10 | `0x0004D930` | `bl` | call | `0x0004D4E8` |
| 11 | `0x0004D934` | `b` | unconditional | `0x0004D93C` |
| 12 | `0x0004D938` | `bl` | call | `0x0004D284` |
| 13 | `0x0004D96C` | `blt` | conditional | `0x0004DA5C` |
| 14 | `0x0004D980` | `beq` | conditional | `0x0004D9B0` |
| 15 | `0x0004D9AC` | `b` | unconditional | `0x0004D9B8` |
| 16 | `0x0004D9C0` | `beq` | conditional | `0x0004DA34` |
| 17 | `0x0004D9D8` | `bne` | conditional | `0x0004DA0C` |
| 18 | `0x0004D9E4` | `bne` | conditional | `0x0004DA0C` |
| 19 | `0x0004DA08` | `b` | unconditional | `0x0004DA24` |
| 20 | `0x0004DA58` | `b` | unconditional | `0x0004DA68` |
