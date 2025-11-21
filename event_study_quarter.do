global RAW  "/Users/yixin/Shaoda Wang/Tax Survey Firm Weibo/Trade War & Lockdown 8.7/Raw Data"
global WORK "/Users/yixin/Shaoda Wang/Tax Survey Firm Weibo/Trade War & Lockdown 8.7/Workdata"
global RES  "/Users/yixin/Shaoda Wang/Tax Survey Firm Weibo/Trade War & Lockdown 8.7/results_quarter_fullsample"

capture mkdir "$RES/onegroup"
capture mkdir "$RES/twogroups"

/*------------------------------------------------------------------------------
* PLOTTING PROGRAMS (1 Group)
*------------------------------------------------------------------------------*/

capture program drop plot_event_study_SA_onegroup
program define plot_event_study_SA_onegroup
    syntax, graph_name(string) graph_title(string)
    
    event_plot e(b_iw)#e(V_iw), ///
        stub_lag(D_lag_q#) ///
        stub_lead(D_lead_q#) ///
        plottype(scatter) ciplottype(rcap) trimlead(4) trimlag(4) noautolegend ///
        graph_opt(title("`graph_title'", size(large)) ///
            xtitle("Quarters since lockdown", size(medlarge)) ///
            ytitle("SA Coefficient", size(medlarge)) ///
            xlabel(-4(1)4, labsize(medium)) ylabel(, labsize(medium) angle(horizontal)) ///
            xline(-1, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8)) ///
            legend(off) ///
            graphregion(color(white)) plotregion(color(white))) ///
        lag_opt1(msymbol(O) color(navy)) ///
        lag_ci_opt1(color(navy%40))

    capture graph export "$RES/onegroup/`graph_name'_SA_quarter.pdf", replace
    capture graph export "$RES/onegroup/`graph_name'_SA_quarter.png", width(2400) replace
    if _rc == 0 di as result "✓ onegroup/`graph_name'_SA_quarter saved"
    else di as error "✗ onegroup/`graph_name'_SA_quarter failed"
end

/*------------------------------------------------------------------------------
* PLOTTING PROGRAMS (2 Groups)
*------------------------------------------------------------------------------*/

capture program drop plot_event_study_SA_twogroups
program define plot_event_study_SA_twogroups
    syntax, graph_name(string) graph_title(string)
    
    event_plot e(b_iw)#e(V_iw) e(b_iw)#e(V_iw), ///
        stub_lag(mfg_D_lag_q# nonmfg_D_lag_q#) ///
        stub_lead(mfg_D_lead_q# nonmfg_D_lead_q#) ///
        plottype(scatter) ciplottype(rcap) together perturb(-0.1 0.1) trimlead(4) trimlag(4) noautolegend ///
        graph_opt(title("`graph_title'", size(large)) ///
            xtitle("Quarters since lockdown", size(medlarge)) ///
            ytitle("SA Coefficient", size(medlarge)) ///
            xlabel(-4(1)4, labsize(medium)) ylabel(, labsize(medium) angle(horizontal)) ///
            legend(order(1 "Manufacturing (13-43)" 3 "Non-manufacturing") position(6) rows(1) size(medium)) ///
            xline(-1, lcolor(gs8) lpattern(dash)) yline(0, lcolor(gs8)) ///
            graphregion(color(white)) plotregion(color(white))) ///
        lag_opt1(msymbol(O) color(blue)) ///
        lag_ci_opt1(color(blue%40)) ///
        lag_opt2(msymbol(triangle) color(red)) ///
        lag_ci_opt2(color(red%40))

    capture graph export "$RES/twogroups/`graph_name'_SA_twogroups_quarter.pdf", replace
    capture graph export "$RES/twogroups/`graph_name'_SA_twogroups_quarter.png", width(2400) replace
    if _rc == 0 di as result "✓ twogroups/`graph_name'_SA_twogroups_quarter saved"
    else di as error "✗ twogroups/`graph_name'_SA_twogroups_quarter failed"
end

/*------------------------------------------------------------------------------
* DATA PREPARATION
*------------------------------------------------------------------------------*/

capture program drop prepare_event_data_quarter
program define prepare_event_data_quarter
    
    * Calculate event time in quarters
    gen event_time_q = yq(year, quarter) - treat_onset_yq if !missing(treat_onset_yq)
    
    * Generate event study dummies (quarterly)
    gen D_lead_q4  = (event_time_q == -4 & event_time_q != .)
    gen D_lead_q3  = (event_time_q == -3 & event_time_q != .)
    gen D_lead_q2  = (event_time_q == -2 & event_time_q != .)
    gen D_lead_q1  = (event_time_q == -1 & event_time_q != .)
    gen D_lag_q0 = (event_time_q == 0 & event_time_q != .)
    gen D_lag_q1 = (event_time_q == 1 & event_time_q != .)
    gen D_lag_q2 = (event_time_q == 2 & event_time_q != .)
    gen D_lag_q3 = (event_time_q == 3 & event_time_q != .)
    gen D_lag_q4 = (event_time_q == 4 & event_time_q != .)
    replace D_lead_q1 = 0  // Baseline period
    
    * Generate industry groups for two-group analysis
    gen mfg = (inrange(indus, 13, 43))
    gen nonmfg = 1 - mfg
    
    * Define control cohort
    sum treat_onset_yq
    gen lastcohort = (never_treated == 1)
    if r(N) > 0 {
        local max_yq = r(max)
        replace lastcohort = (treat_onset_yq == `max_yq') if lastcohort == 0
    }
    
    * Generate interaction terms for two groups
    foreach var in D_lag_q4 D_lag_q3 D_lag_q2 D_lag_q1 ///
                   D_lead_q0 D_lead_q1 D_lead_q2 D_lead_q3 D_lead_q4{
        gen mfg_`var' = mfg * `var'
        gen nonmfg_`var' = nonmfg * `var'
    }
    
    * Generate year-quarter FE
	drop year_quarter
    gen year_quarter = yq(year, quarter)
end

/*------------------------------------------------------------------------------
* ANALYSIS (1 Group)
*------------------------------------------------------------------------------*/

di _n "=========================================="
di "Starting ONE GROUP Analysis (Quarter Level)"
di "=========================================="

use "$WORK/analysis_panel_quarter.dta", clear
prepare_event_data_quarter

* Define outcome variables
local outcomes ///
    post_count ///
    cat1_posts cat2_posts cat3_posts ///
    cat1_pos cat1_neg cat2_pos cat2_neg cat3_pos cat3_neg ///
    pos_share_all neg_share_all ///
    cat1_share_pos_all cat1_share_neg_all ///
    cat2_share_pos_all cat2_share_neg_all ///
    cat3_share_pos_all cat3_share_neg_all

foreach var in `outcomes' {
    di as text "Processing ONE GROUP: `var'"
    
    eventstudyinteract `var' D_lag_q4 D_lag_q3 D_lag_q2 D_lag_q1 D_lag_q0///
        D_lead_q1 D_lead_q2 D_lead_q3 D_lead_q4, ///
        vce(cluster cityid) absorb(user_id year_quarter indus) ///
        cohort(treat_onset_yq) control_cohort(lastcohort)
    
    plot_event_study_SA_onegroup, graph_name("`var'") graph_title("`var'")
    
    di as result "✓ ONE GROUP `var' completed"
}

/*------------------------------------------------------------------------------
* ANALYSIS (2 Groups)
*------------------------------------------------------------------------------*/

di _n "=========================================="
di "Starting TWO GROUPS Analysis (Quarter Level)"
di "=========================================="

foreach var in `outcomes' {
    di as text "Processing TWO GROUPS: `var'"
    
    eventstudyinteract `var' mfg_* nonmfg_*, ///
        vce(cluster cityid) absorb(user_id year_quarter indus) ///
        cohort(treat_onset_yq) control_cohort(lastcohort)
    
    plot_event_study_SA_twogroups, graph_name("`var'") graph_title("`var' - Mfg vs Non-mfg")
    
    di as result "✓ TWO GROUPS `var' completed"
}


di _n "=========================================="
di as result "All analyses completed!"
