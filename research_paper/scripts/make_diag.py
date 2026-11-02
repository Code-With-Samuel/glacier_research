from pathlib import Path

import pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / 'research_paper' / 'figures'
OUT_DIR.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':8.5,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':6.5,'pdf.fonttype':42})
df=pd.read_csv(PROJECT_ROOT / 'processed_data' / 'hkh_glacier_mass_change_era5land_hydrological_year_eda.csv')
g=df.groupby('hydrological_year')[['t2m','u10','tp','ssr']].mean()
base=g.loc[1991:2021]
fig,axs=plt.subplots(1,3,figsize=(7.2,2.1))
for a,(v,lab) in zip(axs,[('t2m','Annual mean t2m (K)'),('u10','Annual mean u10 (m s$^{-1}$)'),('tp','Annual total tp (m)')]):
    a.axvspan(2022.5,2024.5,color='#fb6a4a',alpha=0.25,label='HY with replaced months')
    a.plot(g.index,g[v],'-o',ms=2.5,lw=1,color='#08519c')
    mu,sd=base[v].mean(),base[v].std()
    a.axhline(mu,color='k',lw=0.6,ls='--');a.axhspan(mu-2*sd,mu+2*sd,color='grey',alpha=0.2,label='1991–2021 mean ±2 SD')
    a.set_xlabel('Hydrological year');a.set_ylabel(lab);a.set_xlim(1990.5,2024.5)
axs[0].legend(loc='lower left',fontsize=5.5)
axs[0].set_title('(a) 2-m temperature');axs[1].set_title('(b) 10-m zonal wind');axs[2].set_title('(c) Total precipitation')
fig.tight_layout();fig.savefig(OUT_DIR / 'fig_era5_discontinuity.pdf',bbox_inches='tight')
z=(g.loc[2022:2024]-base.mean())/base.std();print(z.round(2));print(g.loc[2022:2024].round(3));print(base.mean().round(3),base.std().round(3))
