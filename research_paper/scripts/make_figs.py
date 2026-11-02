from pathlib import Path

import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.patches as mp
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import geopandas as gpd, geodatasets, warnings; warnings.filterwarnings('ignore')
from shapely.geometry import box
from shapely.ops import unary_union
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':8.5,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,'pdf.fonttype':42})
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / 'research_paper' / 'figures'
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = str(OUT_DIR) + '/'
df=pd.read_csv(PROJECT_ROOT / 'processed_data' / 'hkh_glacier_mass_change_era5land_hydrological_year_eda.csv')
m=df.glacier_mass_change_mwe
df['cls']=np.select([m>0.1,m<-0.1],['Mass gain','Mass loss'],'Near balance')
CC={'Mass gain':'#2b83ba','Mass loss':'#d7191c','Near balance':'#fdae61'}
world=gpd.read_file(geodatasets.get_path('naturalearth.land'))
cells=df.groupby(['target_latitude','target_longitude']).agg(mean_m=('glacier_mass_change_mwe','mean'),area=('glacier_area_km2','mean')).reset_index()
dom=df.groupby(['target_latitude','target_longitude'])['cls'].agg(lambda s:s.value_counts().idxmax()).reset_index(name='dom')
cells=cells.merge(dom)
polys=[box(lo-0.25,la-0.25,lo+0.25,la+0.25) for la,lo in zip(cells.target_latitude,cells.target_longitude)]
footprint=unary_union(polys).buffer(0.6).buffer(-0.6)   # smoothed envelope of occupied cells
# ---------- Fig 1 study area map (two panels) ----------
import matplotlib.patheffects as pe
from matplotlib.collections import PatchCollection
from shapely.geometry import Polygon
hull=unary_union(polys).buffer(0.9)
hull=unary_union([Polygon(g.exterior) for g in (hull.geoms if hasattr(hull,'geoms') else [hull])])
yrs=df.assign(loss=(df.cls=='Mass loss')).groupby(['target_latitude','target_longitude'])['loss'].sum().reset_index(name='loss_years')
cells=cells.merge(yrs)
fig,axs=plt.subplots(1,2,figsize=(7.2,2.75),sharey=True)
ext=(64,106,25.5,41.5)
def base(ax):
    world.plot(ax=ax,color='#f4f1ea',edgecolor='#8c8c8c',linewidth=0.4,zorder=1)
    gpd.GeoSeries([hull]).plot(ax=ax,color='#7ccba2',alpha=0.40,edgecolor='#1b7a4a',linewidth=1.0,zorder=2)
    ax.set_xlim(ext[0],ext[1]);ax.set_ylim(ext[2],ext[3]);ax.set_aspect(1/np.cos(np.deg2rad(33)))
    ax.grid(alpha=0.25,lw=0.4,zorder=0);ax.set_xlabel('Longitude (°E)')
def cellpatches(vals,cmap,vmin,vmax,ax):
    pc=PatchCollection([Rectangle((lo-0.25,la-0.25),0.5,0.5) for la,lo in zip(cells.target_latitude,cells.target_longitude)],cmap=cmap,edgecolor='none',zorder=3)
    pc.set_array(np.asarray(vals));pc.set_clim(vmin,vmax);ax.add_collection(pc);return pc
for ax in axs: base(ax)
axs[0].set_ylabel('Latitude (°N)')
pc0=cellpatches(cells.mean_m,'RdYlBu',-1.2,1.2,axs[0])
pc1=cellpatches(cells.loss_years,'YlOrRd',0,34,axs[1])
cb=fig.colorbar(pc0,ax=axs[0],orientation='horizontal',fraction=0.07,pad=0.22);cb.set_label('Mean specific mass change, 1991–2024 (m w.e.)',fontsize=6.5);cb.ax.tick_params(labelsize=6)
cb=fig.colorbar(pc1,ax=axs[1],orientation='horizontal',fraction=0.07,pad=0.22);cb.set_label('Years (of 34) classed as mass loss',fontsize=6.5);cb.ax.tick_params(labelsize=6)
axs[0].set_title('(a) Mean mass change per 0.5° cell',fontsize=8);axs[1].set_title('(b) Frequency of mass-loss class per cell',fontsize=8)
halo=[pe.withStroke(linewidth=1.8,foreground='white')]
for ax in axs:
    for nm,x,y in [('Karakoram',76.3,37.3),('Hindu Kush',69.6,35.2),('Himalaya',84,28.0),('Tibetan Plateau',89,35.0),('Tien Shan',77,40.6),('Hengduan',99.0,26.6)]:
        ax.text(x,y,nm,fontsize=6,style='italic',weight='bold',color='#14532d',ha='center',zorder=6,path_effects=halo)
fig.subplots_adjust(wspace=0.04,bottom=0.05);fig.savefig(OUT+'fig_study_area_map.pdf',bbox_inches='tight');plt.close()
# ---------- Fig 2 colourful workflow ----------
fig,ax=plt.subplots(figsize=(7.2,5.6));ax.set_xlim(0,100);ax.set_ylim(-1,71);ax.axis('off')
def box_(x,y,w,h,txt,col,fs=6.4,tc='k'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.2,rounding_size=1.2',fc=col,ec='#333',lw=0.8,zorder=3))
    ax.text(x+w/2,y+h/2,txt,ha='center',va='center',fontsize=fs,color=tc,zorder=4)
def arr(pts,c='#333'):
    for (x1,y1),(x2,y2) in zip(pts[:-2],pts[1:-1]): ax.plot([x1,x2],[y1,y2],color=c,lw=1.1,zorder=2)
    ax.add_patch(FancyArrowPatch(pts[-2],pts[-1],arrowstyle='-|>',mutation_scale=9,lw=1.1,color=c,zorder=2,shrinkA=0,shrinkB=0))
def lane(y,h,name,col):
    ax.add_patch(Rectangle((0.3,y),99.4,h,fc=col,ec='none',alpha=0.28,zorder=0)); ax.text(1.2,y+h-1.7,name,fontsize=7.4,weight='bold',color='#222',zorder=1)
LY=[54,36,18,0]; LH=16
lane(LY[0],LH,'STAGE 1  Data acquisition','#6baed6');lane(LY[1],LH,'STAGE 2  Integration and quality control','#74c476')
lane(LY[2],LH,'STAGE 3  Target, features and validation design','#fd8d3c');lane(LY[3],LH,'STAGE 4  Modelling, evaluation and reporting','#9e9ac8')
X=[2.5,27.5,52.5,77.5];W=20;H=9.5
def row(i,items,hz=True):
    y=LY[i]+1.3
    for x,(t,c,tc) in zip(X,items): box_(x,y,W,H,t,c,tc=tc)
    if hz:
        for k in range(3): arr([(X[k]+W+0.4,y+H/2),(X[k+1]-0.4,y+H/2)])
row(0,[('ERA5-Land monthly\n15 variables, 0.1°\n(CDS, 1950–present)','#4292c6','w'),('ECMWF recovery CSV\nSep 2022–Feb 2024\n12 affected variables','#ef3b2c','w'),('C3S/WGMS gridded\nmass change, 0.5°\n1991–2024 (target)','#4292c6','w'),('Glacier area (km²)\nand uncertainty\n(target product)','#4292c6','w')],hz=False)
row(1,[('Replace 12 variables\n(year-month + cell);\nsnowc, sde, sd kept','#41ab5d','k'),('Conservative area-\nweighted regridding\n(overlap ≥ 70 %)','#41ab5d','k'),('April–March hydro-\nlogical-year aggregate\n(mean / sum / flux)','#41ab5d','k'),('Join on cell + year\n23,698 rows, 697 cells\n34 years, 0 unmatched','#238b45','w')])
row(2,[('Three-class target\ngain > +0.1, loss < −0.1,\nelse near balance','#fd8d3c','k'),('17 predictors\n(area, year, 15 climate)\ncoordinates excluded','#fd8d3c','k'),('K-means, k = 25\non 697 locations\n(seed 42, n_init 20)','#fdae6b','k'),('StratifiedGroupKFold\n5 folds, clusters whole\n0 shared clusters','#e6550d','w')])
row(3,[('LR · SVM (RBF)\nRandom Forest\nGradient Boosting','#9e9ac8','k'),('21 configurations\n× 5 folds = 105 fits\nselect by macro-F1','#9e9ac8','k'),('Pooled OOF metrics,\nconfusion matrices,\nROC-AUC','#756bb1','w'),('Limits: retrospective;\nsame folds for tuning;\nno nested CV / test','#54278f','w')])
# vertical links / elbows
yc=lambda i:LY[i]+1.3+H/2
g0=(LY[0]+LY[1]+LH)/2
arr([(X[0]+W/2,LY[0]+1.3-0.2),(X[0]+W/2,LY[1]+1.3+H+0.2)])
arr([(X[1]+W/2,LY[0]+1.3-0.2),(X[1]+W/2,g0),(X[0]+W/2+6,g0),(X[0]+W/2+6,LY[1]+1.3+H+0.2)],c='#b2182b')
arr([(X[2]+W/2,LY[0]+1.3-0.2),(X[2]+W/2,g0),(X[3]+W/2-6,g0),(X[3]+W/2-6,LY[1]+1.3+H+0.2)])
arr([(X[3]+W/2+4,LY[0]+1.3-0.2),(X[3]+W/2+4,LY[1]+1.3+H+0.2)])
# bus joins: S2 join -> S3 target ; S3 split-> S4 models
gap1=(LY[2]+LH+LY[1])/2; gap2=(LY[3]+LH+LY[2])/2
arr([(X[3]+W/2,LY[1]+1.3-0.2),(X[3]+W/2,gap1+0.0),(X[0]+W/2,gap1),(X[0]+W/2,LY[2]+1.3+H+0.2)],c='#1b5e20')
arr([(X[3]+W/2,LY[2]+1.3-0.2),(X[3]+W/2,gap2),(X[0]+W/2,gap2),(X[0]+W/2,LY[3]+1.3+H+0.2)],c='#7f2704')
fig.savefig(OUT+'fig_workflow.pdf',bbox_inches='tight');plt.close()
# ---------- Fig 3 problem statement ----------
yr=df.groupby('hydrological_year')['glacier_mass_change_mwe'].agg(['mean',lambda s:s.quantile(.1),lambda s:s.quantile(.9)]);yr.columns=['mean','p10','p90']
share=pd.crosstab(df.hydrological_year,df.cls,normalize='index')[['Mass loss','Near balance','Mass gain']]*100
fig,axs=plt.subplots(1,3,figsize=(7.2,2.45))
a=axs[0];a.fill_between(yr.index,yr.p10,yr.p90,color='#9ecae1',alpha=0.6,label='10–90th percentile across cells');a.plot(yr.index,yr['mean'],color='#08519c',lw=1.4,label='Mean');a.axhspan(-0.1,0.1,color='#fdae61',alpha=0.35,label='Near-balance band ±0.1');a.axhline(0,color='k',lw=0.4)
a.set_xlabel('Hydrological year');a.set_ylabel('Mass change (m w.e.)');a.set_title('(a) Spatio-temporal heterogeneity');a.legend(loc='lower left',fontsize=5.5)
a=axs[1];tot=df.cls.value_counts();a.bar(['Loss','Gain','Near\nbalance'],[tot['Mass loss'],tot['Mass gain'],tot['Near balance']],color=[CC['Mass loss'],CC['Mass gain'],CC['Near balance']],edgecolor='k',lw=0.5)
for i,v in enumerate([tot['Mass loss'],tot['Mass gain'],tot['Near balance']]):a.text(i,v+250,f'{v:,}\n({100*v/len(df):.1f} %)',ha='center',fontsize=6)
a.set_ylim(0,19500);a.set_ylabel('Records');a.set_title('(b) Class imbalance')
a=axs[2];a.stackplot(share.index,share['Mass loss'],share['Near balance'],share['Mass gain'],colors=[CC['Mass loss'],CC['Near balance'],CC['Mass gain']],labels=['Loss','Near balance','Gain']);a.axvspan(2021.5,2024.5,color='k',alpha=0.12);a.text(2022.3,50,'2022–24:\nno/negligible\ngain & near\nbalance',fontsize=5.5,rotation=90,va='center',ha='center')
a.set_xlim(1991,2024);a.set_ylim(0,100);a.set_xlabel('Hydrological year');a.set_ylabel('Share of cells (%)');a.set_title('(c) Distribution shift');a.legend(loc='lower left',fontsize=5.5)
fig.tight_layout();fig.savefig(OUT+'fig_problem_statement.pdf',bbox_inches='tight');plt.close()
# ---------- Fig 4 target distribution with uncertainty ----------
fig,axs=plt.subplots(1,3,figsize=(7.2,2.3))
a=axs[0];bins=np.linspace(-2.2,1.2,69);a.hist(m,bins=bins,color='#7fa7c9',edgecolor='white',lw=0.2)
a.axvspan(-0.1,0.1,color='#fdae61',alpha=0.5);a.axvline(m.mean(),color='k',ls='--',lw=0.8);a.set_xlabel('Specific mass change (m w.e.)');a.set_ylabel('Records');a.set_title('(a) Target distribution')
a.text(m.mean()-0.05,a.get_ylim()[1]*0.9,f'mean {m.mean():.3f}',fontsize=6,ha='right')
a=axs[1];u=df.uncertainty_mwe;a.hist(u,bins=np.linspace(0,1.2,61),color='#c7a2d6',edgecolor='white',lw=0.2);a.axvline(0.1,color='#e6550d',lw=1.2,label='Class half-width 0.1');a.axvline(u.median(),color='k',ls='--',lw=0.8,label=f'Median {u.median():.3f}');a.set_xlabel('Reported uncertainty (m w.e.)');a.set_ylabel('Records');a.set_title('(b) Label uncertainty');a.legend(fontsize=6)
a=axs[2];nb=df[df.cls=='Near balance'];samp=df.sample(4000,random_state=1);a.scatter(samp.glacier_mass_change_mwe,samp.uncertainty_mwe,s=2,alpha=0.4,color='#4a4a8a');a.axhline(0.1,color='#e6550d',lw=0.8);a.axvspan(-0.1,0.1,color='#fdae61',alpha=0.4);a.set_xlim(-2.2,1.2);a.set_ylim(0,1.2);a.set_xlabel('Mass change (m w.e.)');a.set_ylabel('Uncertainty (m w.e.)');a.set_title('(c) Value vs. uncertainty (4,000 random records)')
fig.tight_layout();fig.savefig(OUT+'fig_target_uncertainty.pdf',bbox_inches='tight');plt.close()
# ---------- Fig 5 class share per year (stacked bars, counts) ----------
fig,a=plt.subplots(figsize=(3.45,2.3))
cnt=pd.crosstab(df.hydrological_year,df.cls)[['Mass loss','Near balance','Mass gain']]
b=np.zeros(len(cnt))
for k in cnt.columns:
    a.bar(cnt.index,cnt[k],bottom=b,color=CC[k],label=k,width=0.9,edgecolor='white',lw=0.2);b+=cnt[k].values
a.set_xlabel('Hydrological year');a.set_ylabel('Cells per class (of 697)');a.legend(ncol=3,fontsize=6,loc='upper center',bbox_to_anchor=(0.5,1.18),frameon=False)
fig.tight_layout();fig.savefig(OUT+'fig_class_per_year.pdf',bbox_inches='tight');plt.close()
# ---------- Fig 6 correlation heatmap ----------
feats=['glacier_area_km2','hydrological_year','t2m','snowc','sde','sd','sf','smlt','ssr','str','ro','es','sro','e','u10','v10','tp']
C=df[feats+['glacier_mass_change_mwe']].corr()
fig,a=plt.subplots(figsize=(7.2,4.8));im=a.imshow(C.values,cmap='RdBu_r',vmin=-1,vmax=1)
lab=['area','year','t2m','snowc','sde','sd','sf','smlt','ssr','str','ro','es','sro','e','u10','v10','tp','target']
a.set_xticks(range(18));a.set_xticklabels(lab,rotation=90,fontsize=7);a.set_yticks(range(18));a.set_yticklabels(lab,fontsize=7)
for i in range(C.shape[0]):
    for j in range(C.shape[1]):
        value = C.iat[i, j]
        text_color = 'white' if abs(value) >= 0.55 else '#222222'
        a.text(j, i, f'{value:.2f}', ha='center', va='center',
               fontsize=6, color=text_color)
a.axhline(16.5,color='k',lw=0.6);a.axvline(16.5,color='k',lw=0.6)
cb=fig.colorbar(im,fraction=0.046,pad=0.02);cb.set_label('Pearson r',fontsize=8);cb.ax.tick_params(labelsize=7)
fig.tight_layout();fig.savefig(OUT+'fig_correlation.pdf',bbox_inches='tight');plt.close()
C.round(3).to_csv(OUT+'correlation_matrix.csv')
print(C['glacier_mass_change_mwe'].round(3).to_dict())
big=C.iloc[:17,:17].abs().where(~np.eye(17,dtype=bool));print((big>0.8).sum().sum()//2, 'pairs |r|>0.8');
import itertools
for i,j in itertools.combinations(range(17),2):
    if abs(C.iloc[i,j])>0.8: print(feats[i],feats[j],round(C.iloc[i,j],3))
# ---------- Fig 7 area by class + monthly? predictors by class ----------
fig,axs=plt.subplots(1,3,figsize=(7.2,2.2))
for a,f,t in zip(axs,['t2m','snowc','smlt'],['t2m (K)','snowc (as exported)','smlt (m w.e. per day, monthly-mean sum)']):
    data=[df.loc[df.cls==k,f] for k in ['Mass gain','Near balance','Mass loss']]
    bp=a.boxplot(data,tick_labels=['Gain','Near\nbal.','Loss'],patch_artist=True,showfliers=False,widths=0.6)
    for p,k in zip(bp['boxes'],['Mass gain','Near balance','Mass loss']):p.set_facecolor(CC[k])
    a.set_title(t,fontsize=7)
fig.tight_layout();fig.savefig(OUT+'fig_predictors_by_class.pdf',bbox_inches='tight');plt.close()
print(df.groupby('cls')[['t2m','snowc','smlt','glacier_area_km2']].median().round(3))
# label ambiguity numbers
amb=(m.abs()<=df.uncertainty_mwe)
print('abs(m)<=u share',amb.mean(), ' per class', amb.groupby(df.cls).mean().round(3).to_dict())
print('near-balance with u>0.1',(df[df.cls=="Near balance"].uncertainty_mwe>0.1).mean())
print('class flips possible: |m|-0.1 within u', ((m.abs()-0.1).abs()<=df.uncertainty_mwe).mean())
