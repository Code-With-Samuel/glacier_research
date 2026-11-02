from pathlib import Path

import numpy as np, json, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = PROJECT_ROOT / 'research_paper' / 'figures'
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT = str(OUT_DIR) + '/'
fold_f1_path = OUT_DIR / 'fold_f1.json'
if fold_f1_path.exists():
    with fold_f1_path.open(encoding='utf-8') as fold_f1_file:
        ff=json.load(fold_f1_file)
else:
    spatial_cv_dir = PROJECT_ROOT / 'spatial_cv_outputs'
    candidate_path = spatial_cv_dir / 'spatial_cv_candidate_results.csv'
    fold_metrics_path = spatial_cv_dir / 'spatial_cv_fold_metrics.csv'
    missing_paths = [path for path in (candidate_path, fold_metrics_path) if not path.exists()]
    if missing_paths:
        expected = ', '.join(str(path) for path in missing_paths)
        raise FileNotFoundError(
            f"Missing spatial-CV results: {expected}. Run "
            "'supervised_learning_for_classification.ipynb' from the repository "
            "root, or provide research_paper/figures/fold_f1.json."
        )

    candidate_results = pd.read_csv(candidate_path)
    fold_metrics = pd.read_csv(fold_metrics_path)
    best_candidates = candidate_results.sort_values(
        [
            'mean_validation_macro_f1',
            'mean_validation_balanced_accuracy',
            'mean_validation_accuracy',
        ],
        ascending=False,
    ).drop_duplicates('model').set_index('model')
    ff = {}
    for model_name in [
        'Gradient Boosting',
        'Random Forest',
        'SVM (RBF)',
        'Logistic Regression',
    ]:
        if model_name not in best_candidates.index:
            raise ValueError(f"Spatial-CV candidate results are missing {model_name}.")
        candidate = best_candidates.loc[model_name, 'candidate']
        selected_folds = fold_metrics.loc[
            (fold_metrics['model'] == model_name)
            & (fold_metrics['candidate'] == candidate)
        ].sort_values('fold')
        if len(selected_folds) != 5:
            raise ValueError(
                f"Expected five selected validation folds for {model_name}; "
                f"found {len(selected_folds)}."
            )
        ff[model_name] = selected_folds['validation_macro_f1'].tolist()
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':8,'axes.titlesize':8.5,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':6.5,'pdf.fonttype':42})
M=['Gradient Boosting','Random Forest','SVM (RBF)','Logistic Regression']
COL={'Gradient Boosting':'#1b9e77','Random Forest':'#d95f02','SVM (RBF)':'#7570b3','Logistic Regression':'#e7298a'}
SH={'Gradient Boosting':'GB','Random Forest':'RF','SVM (RBF)':'SVM','Logistic Regression':'LR'}
# --- model comparison: pooled OOF
acc=[0.683897,0.647607,0.519200,0.511858];ba=[0.629690,0.538174,0.474721,0.436796];f1=[0.603683,0.529369,0.447050,0.418021];auc=[0.837258,0.765437,0.679610,0.652629]
fig,ax=plt.subplots(figsize=(3.45,2.5));x=np.arange(4);w=0.2
for k,(v,l,c) in enumerate([(acc,'Accuracy','#9ecae1'),(ba,'Balanced acc.','#4292c6'),(f1,'Macro-F1','#08519c'),(auc,'Macro OvR AUC','#fdae6b')]):
    b=ax.bar(x+(k-1.5)*w,v,w,label=l,color=c,edgecolor='k',lw=0.3)
    for xi,vi in zip(x+(k-1.5)*w,v): ax.text(xi,vi+0.008,f'{vi:.2f}',ha='center',fontsize=4.8,rotation=90)
ax.axhline(15344/23698,color='k',ls=':',lw=0.8,label='All-loss accuracy (0.648)')
ax.set_xticks(x);ax.set_xticklabels([SH[m] for m in M]);ax.set_ylim(0,1.0);ax.set_ylabel('Score (pooled spatial OOF)');ax.legend(ncol=3,fontsize=5.3,loc='lower center',bbox_to_anchor=(0.5,1.0),frameon=False)
fig.tight_layout();fig.savefig(OUT+'fig_model_comparison.pdf',bbox_inches='tight');plt.close()
# --- fold-level dots
fig,ax=plt.subplots(figsize=(3.45,2.3))
for i,m in enumerate(M):
    v=ff[m];ax.plot([i]*5,v,'o',color=COL[m],ms=4,alpha=0.85,markeredgecolor='k',markeredgewidth=0.3)
    ax.hlines(np.mean(v),i-0.25,i+0.25,color='k',lw=1.3);ax.text(i+0.28,np.mean(v),f'{np.mean(v):.3f}',fontsize=6,va='center')
for f in range(5):
    ax.plot(range(4),[ff[m][f] for m in M],color='grey',lw=0.4,alpha=0.6)
ax.set_xticks(range(4));ax.set_xticklabels([SH[m] for m in M]);ax.set_ylabel('Validation macro-F1 per spatial fold');ax.set_xlim(-0.5,3.9);ax.set_ylim(0.34,0.70)
fig.tight_layout();fig.savefig(OUT+'fig_fold_scores.pdf',bbox_inches='tight');plt.close()
# --- confusion matrices (counts read from notebook figure; row-normalised colouring)
CM={'Gradient Boosting':[[3265,359,1352],[969,11255,3120],[895,796,1687]],'Random Forest':[[2846,1147,983],[1694,11514,2136],[1012,1379,987]],'SVM (RBF)':[[2347,943,1686],[2799,8642,3903],[1141,922,1315]],'Logistic Regression':[[2424,1308,1244],[3796,8880,2668],[1389,1163,826]]}
json.dump(CM,open(OUT+'confusion_counts.json','w'))
fig,axs=plt.subplots(1,4,figsize=(7.2,2.0))
lab=['Gain','Loss','Near\nbal.']
for ax,m in zip(axs,M):
    c=np.array(CM[m]);r=c/c.sum(1,keepdims=True)
    ax.imshow(r,cmap='Blues',vmin=0,vmax=1)
    for i in range(3):
        for j in range(3): ax.text(j,i,f'{c[i,j]:,}\n({100*r[i,j]:.0f}%)',ha='center',va='center',fontsize=5.4,color='w' if r[i,j]>0.55 else 'k')
    ax.set_xticks(range(3));ax.set_xticklabels(lab);ax.set_yticks(range(3));ax.set_yticklabels(lab if m==M[0] else ['']*3);ax.set_title(m,fontsize=7.5);ax.set_xlabel('Predicted')
axs[0].set_ylabel('True class')
fig.tight_layout();fig.savefig(OUT+'fig_confusion.pdf',bbox_inches='tight');plt.close()
# --- per-class P/R/F1 heatmap
PC={'Gradient Boosting':[[.64,.66,.65],[.91,.73,.81],[.27,.50,.35]],'Random Forest':[[.51,.57,.54],[.82,.75,.78],[.24,.29,.26]],'SVM (RBF)':[[.37,.47,.42],[.82,.56,.67],[.19,.39,.26]],'Logistic Regression':[[.32,.49,.39],[.78,.58,.67],[.17,.24,.20]]}
fig,axs=plt.subplots(1,3,figsize=(7.2,1.9),sharey=True)
for k,(ax,nm) in enumerate(zip(axs,['Precision','Recall','F1-score'])):
    A=np.array([[PC[m][c][k] for c in range(3)] for m in M])
    im=ax.imshow(A,cmap='YlGnBu',vmin=0,vmax=1)
    for i in range(4):
        for j in range(3): ax.text(j,i,f'{A[i,j]:.2f}',ha='center',va='center',fontsize=7,color='w' if A[i,j]>0.6 else 'k')
    ax.set_xticks(range(3));ax.set_xticklabels(['Gain','Loss','Near bal.']);ax.set_yticks(range(4));ax.set_yticklabels([SH[m] for m in M]);ax.set_title(nm)
fig.tight_layout();fig.savefig(OUT+'fig_perclass.pdf',bbox_inches='tight');plt.close()
# --- train vs validation (selected configs, fold means)
trF=[0.714612,0.795716,0.527641,0.433565];vaF=[0.595909,0.522762,0.431517,0.404179];trA=[0.770887,0.828815,0.588036,0.527137];vaA=[0.688090,0.655657,0.525904,0.519936]
fig,axs=plt.subplots(1,2,figsize=(3.45*1.0,2.2),sharey=True)
for ax,(tr,va,t) in zip(axs,[(trF,vaF,'Macro-F1'),(trA,vaA,'Accuracy')]):
    x=np.arange(4);ax.bar(x-0.19,tr,0.38,color='#bdbdbd',edgecolor='k',lw=0.3,label='Train');ax.bar(x+0.19,va,0.38,color=[COL[m] for m in M],edgecolor='k',lw=0.3,label='Validation')
    for xi,a,b in zip(x,tr,va): ax.text(xi,max(a,b)+0.02,f'Δ{a-b:+.2f}',ha='center',fontsize=5.5)
    ax.set_xticks(x);ax.set_xticklabels([SH[m] for m in M],fontsize=6);ax.set_title(t);ax.set_ylim(0,1)
axs[0].set_ylabel('Mean over 5 folds');axs[0].legend(fontsize=5.5,loc='upper right')
fig.tight_layout();fig.savefig(OUT+'fig_train_val.pdf',bbox_inches='tight');plt.close()
# --- hyperparameter sensitivity GB and RF
gb=[('0.05/2/100',0.509454),('0.05/2/200',0.547055),('0.05/3/100',0.553723),('0.05/3/200',0.577913),('0.10/2/100',0.547404),('0.10/2/200',0.573568),('0.10/3/100',0.578288),('0.10/3/200',0.595909)]
rf=[('12/1/150',0.519835),('12/1/300',0.520764),('12/3/150',0.521779),('12/3/300',0.522762),('None/1/150',0.457280),('None/1/300',0.452012),('None/3/150',0.520169),('None/3/300',0.518401)]
rftr=[0.817012,0.821310,0.793059,0.795716,1.0,1.0,0.989563,0.990540]
fig,axs=plt.subplots(1,2,figsize=(7.2,2.2))
a=axs[0];a.bar(range(8),[v for _,v in gb],color=['#1b9e77' if i==7 else '#a6dba0' for i in range(8)],edgecolor='k',lw=0.3)
a.set_xticks(range(8));a.set_xticklabels([l for l,_ in gb],rotation=45,ha='right',fontsize=6);a.set_ylim(0.45,0.63);a.set_ylabel('Mean validation macro-F1');a.set_xlabel('Gradient Boosting: learning rate / depth / trees');a.set_title('(a) GB sensitivity (best at grid edge)')
for i,(_,v) in enumerate(gb): a.text(i,v+0.003,f'{v:.3f}',ha='center',fontsize=5.5)
a=axs[1];x=np.arange(8);a.bar(x-0.2,rftr,0.4,color='#bdbdbd',edgecolor='k',lw=0.3,label='Train macro-F1');a.bar(x+0.2,[v for _,v in rf],0.4,color='#d95f02',edgecolor='k',lw=0.3,label='Validation macro-F1')
a.set_xticks(x);a.set_xticklabels([l for l,_ in rf],rotation=45,ha='right',fontsize=6);a.set_ylim(0,1.12);a.set_xlabel('Random Forest: max depth / min leaf / trees');a.set_title('(b) RF overfitting when depth unlimited');a.legend(fontsize=5.5,loc='upper left',ncol=2)
fig.tight_layout();fig.savefig(OUT+'fig_hyperparam.pdf',bbox_inches='tight');plt.close()
# --- AUC per class
A={'Gradient Boosting':[.899519,.885820,.726434],'Random Forest':[.821460,.806660,.668192],'SVM (RBF)':[.716192,.737973,.584665],'Logistic Regression':[.681500,.689429,.586957]}
fig,ax=plt.subplots(figsize=(3.45,2.2));x=np.arange(3);w=0.2
for k,m in enumerate(M):
    ax.bar(x+(k-1.5)*w,A[m],w,color=COL[m],edgecolor='k',lw=0.3,label=SH[m])
ax.axhline(0.5,color='k',ls=':',lw=0.8);ax.set_xticks(x);ax.set_xticklabels(['Gain','Loss','Near balance']);ax.set_ylim(0.4,1.0);ax.set_ylabel('One-vs-rest ROC-AUC');ax.legend(ncol=4,fontsize=5.5,loc='upper right')
fig.tight_layout();fig.savefig(OUT+'fig_auc_class.pdf',bbox_inches='tight');plt.close()
# --- cost vs performance (log elapsed minutes, Colab, hardware unspecified)
tm={'Logistic Regression':(0.7,15),'Random Forest':(19.5,40),'SVM (RBF)':(10.5,10),'Gradient Boosting':(63.3,40)}
fig,ax=plt.subplots(figsize=(3.45,2.3))
for m,f in zip(M,f1):
    mins,n=tm[m];per=mins/n;ax.scatter(per,f,s=60,color=COL[m],edgecolor='k',lw=0.5,zorder=3);ax.annotate(SH[m],(per,f),xytext=(4,4),textcoords='offset points',fontsize=7)
ax.set_xscale('log');ax.set_xlabel('Mean wall-clock per fit in search loop (min, log)');ax.set_ylabel('Pooled OOF macro-F1');ax.grid(alpha=0.3);ax.set_ylim(0.38,0.65)
fig.tight_layout();fig.savefig(OUT+'fig_cost_perf.pdf',bbox_inches='tight');plt.close()
for m in M: print(m,tm[m][0]/tm[m][1])
