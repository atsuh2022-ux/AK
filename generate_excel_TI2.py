import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.drawing.image import Image as XLImage
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
rcParams['font.family'] = 'DejaVu Sans'

# ── データ読み込み ──
SRC = '/root/.claude/uploads/8fc6c494-7d22-5ced-b922-3105f12fe0f0/1f63aff1-TI___20260328_20260712.xlsx'
src = openpyxl.load_workbook(SRC)

def ws_to_df(ws):
    data = list(ws.iter_rows(values_only=True))
    df = pd.DataFrame(data[1:], columns=data[0])
    df['日付'] = pd.to_datetime(df['日付'])
    return df

df_cond  = ws_to_df(src['主観的体調'])
df_body  = ws_to_df(src['身体データ'])
df_train = ws_to_df(src['トレーニング'])
df_food  = ws_to_df(src['食事'])

prot_cols = ['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
             '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']
for c in prot_cols:
    df_food[c] = df_food[c].apply(lambda x: 1 if x == '○' else 0)
df_food['タンパク質摂取数'] = df_food[prot_cols].sum(axis=1)
df_food['補食_bin'] = df_food['練習後補食'].apply(lambda x: 1 if x == 'はい' else 0)

df = df_cond.merge(df_body, on='日付', how='outer')
df = df.merge(df_train, on='日付', how='outer')
df = df.merge(df_food[['日付','練習後補食','補食_bin','栄養バランス',
                        '水分摂取量_ml','きのこ海藻','タンパク質摂取数']], on='日付', how='outer')
df = df.sort_values('日付').reset_index(drop=True)

train_only = df[(df['種目'].notna()) & (df['種目'] != '休養日')]

# ── 統計 ──
total_train  = len(train_only)
total_rest   = int((df['種目'] == '休養日').sum())
total_min    = int(df['時間_分'].fillna(0).sum())
avg_rpe      = train_only['RPE'].mean()
avg_fat      = train_only['運動後疲労'].mean()
avg_sleep_h  = df_cond['睡眠時間'].mean()
avg_sleep_q  = df_cond['睡眠の質'].mean()
avg_cd       = df_cond['起床時コンディション'].mean()
avg_wt       = df_body['体重_kg'].mean()
wt_range     = df_body['体重_kg'].max() - df_body['体重_kg'].min()
wt_first, wt_last = df_body['体重_kg'].iloc[0], df_body['体重_kg'].iloc[-1]
snack_yes    = int(df_food['補食_bin'].sum())
water_1000   = int((df_food['水分摂取量_ml'] >= 1000).sum())
kino_yes     = int((df_food['きのこ海藻'] == 'はい').sum())
avg_protein  = df_food['タンパク質摂取数'].mean()
n_total      = len(df_food)

# 前期/後期比較
SPLIT = pd.Timestamp('2026-06-20')
tr_e = train_only[train_only['日付'] <  SPLIT]
tr_l = train_only[train_only['日付'] >= SPLIT]
cd_e = df_cond[df_cond['日付'] <  SPLIT]
cd_l = df_cond[df_cond['日付'] >= SPLIT]

# 関連性
snack_m = df_food.merge(df_train[df_train['種目']!='休養日'][['日付','運動後疲労']], on='日付', how='inner')
snack_yes_fat = snack_m[snack_m['練習後補食']=='はい']['運動後疲労'].mean()
snack_no_fat  = snack_m[snack_m['練習後補食']=='いいえ']['運動後疲労'].mean()

water_m = df_food.merge(df_train[df_train['種目']!='休養日'][['日付','運動後疲労']], on='日付', how='inner')
water_hi = water_m[water_m['水分摂取量_ml']>=1000]['運動後疲労'].mean()
water_lo = water_m[water_m['水分摂取量_ml']<1000]['運動後疲労'].mean()

rows_rpe=[]
for i in range(len(df_train)-1):
    rpe=df_train.iloc[i]['RPE']
    nxt=df_cond[df_cond['日付']==df_train.iloc[i+1]['日付']]['起床時コンディション']
    if len(nxt) and rpe>1: rows_rpe.append({'rpe':rpe,'cd':nxt.iloc[0]})
rc=pd.DataFrame(rows_rpe)
rpe_hi_cd=rc[rc['rpe']>=7]['cd'].mean(); rpe_lo_cd=rc[rc['rpe']<7]['cd'].mean()

rows_sh=[]
for i in range(len(df_cond)-1):
    sh=df_cond.iloc[i]['睡眠時間']
    nf=df_train[df_train['日付']==df_cond.iloc[i+1]['日付']]['運動後疲労']
    if len(nf) and nf.iloc[0]>1: rows_sh.append({'sh':sh,'fat':nf.iloc[0]})
sc=pd.DataFrame(rows_sh)
sh_hi=sc[sc['sh']>=7.5]['fat'].mean(); sh_lo=sc[sc['sh']<7.5]['fat'].mean()

# 週次
df_train2=df_train.copy(); df_train2['wk']=df_train2['日付'].dt.isocalendar().week
weekly=df_train2[df_train2['種目']!='休養日'].groupby('wk').agg(
    days=('日付','count'),total_min=('時間_分','sum'),avg_rpe=('RPE','mean'),avg_fat=('運動後疲労','mean')).reset_index()

print("Stats OK")

# ── カラーパレット ──
C_B='#2E86AB'; C_R='#E84855'; C_G='#3BB273'; C_O='#F4A259'; C_P='#7B2D8B'; C_GR='#8D99AE'
dates=pd.to_datetime(df['日付'])

# ── Fig A: トレンド4パネル ──
fig,axes=plt.subplots(4,1,figsize=(16,18),facecolor='#F8F9FA')
fig.suptitle('TI Athlete — Full Period Trend  2026.03.30 – 2026.07.12',fontsize=14,fontweight='bold',y=0.99)

ax=axes[0]; ax.set_facecolor('#EDF2F4')
ax.plot(dates,df['体重_kg'],color=C_B,lw=2,marker='o',ms=3)
ax.axhline(df_body['体重_kg'].mean(),color=C_GR,ls='--',lw=1,label=f'Avg {avg_wt:.1f}kg')
ax.axvline(SPLIT,color='#E53E3E',ls=':',lw=1.5,label='6/20 (phase split)')
ax.set_title('Body Weight Trend',fontweight='bold'); ax.set_ylabel('kg'); ax.set_ylim(59.5,63.5)
ax.tick_params(axis='x',rotation=45,labelsize=7); ax.legend(fontsize=8)

ax=axes[1]; ax.set_facecolor('#EDF2F4')
ax.plot(dates,df['起床時コンディション'],color=C_G,lw=1.5,marker='o',ms=3,label='Morning Cond (1=best)')
ax.plot(dates,df['睡眠の質'],color=C_P,lw=1.5,marker='^',ms=3,ls='--',label='Sleep Quality (1=best)')
ax.fill_between(dates,df['起床時コンディション'].fillna(0),alpha=0.1,color=C_G)
ax.axhline(3,color='gray',ls=':',lw=1,alpha=0.5)
ax.axvline(SPLIT,color='#E53E3E',ls=':',lw=1.5)
ax.set_title('Morning Condition & Sleep Quality (1=Good / 5=Bad)',fontweight='bold')
ax.set_ylabel('Score'); ax.set_ylim(0,6)
ax.tick_params(axis='x',rotation=45,labelsize=7); ax.legend(fontsize=8)

ax=axes[2]; ax.set_facecolor('#EDF2F4')
x_pos=range(len(dates))
rpe_b=[r if (pd.notna(r) and r>1) else 0 for r in df['RPE']]
fat_v=[f if (pd.notna(f) and f>1) else np.nan for f in df['運動後疲労']]
ax.bar(x_pos,rpe_b,color=C_O,alpha=0.5,width=0.6,label='RPE')
ax.plot(x_pos,fat_v,color=C_R,lw=2,marker='s',ms=3,label='Post-workout Fatigue')
ax.axhline(4,color=C_R,ls=':',lw=1,alpha=0.5)
ax.axvline(list(x_pos)[list(dates).index(min(dates,key=lambda d:abs(d-SPLIT)))],color='#E53E3E',ls=':',lw=1.5)
ax.set_title('RPE & Post-workout Fatigue',fontweight='bold')
ax.set_ylabel('Score'); ax.set_xticks(list(x_pos)[::4])
ax.set_xticklabels([dates.iloc[i].strftime('%m/%d') for i in list(x_pos)[::4]],rotation=45,fontsize=7)
ax.legend(fontsize=8)

ax=axes[3]; ax.set_facecolor('#EDF2F4')
ax.bar(dates,df['睡眠時間'].fillna(0),color=C_B,alpha=0.5,width=0.7,label='Sleep (h)')
ax.plot(dates,df['水分摂取量_ml'].fillna(0)/1000,color=C_G,lw=2,marker='D',ms=3,label='Water (L)')
ax.axhline(7,color=C_O,ls='--',lw=1.5,label='7h sleep')
ax.axhline(1.0,color=C_G,ls=':',lw=1,alpha=0.5)
ax.axvline(SPLIT,color='#E53E3E',ls=':',lw=1.5)
ax.set_title('Sleep Hours & Water Intake',fontweight='bold')
ax.set_ylabel('h / L'); ax.set_ylim(0,10)
ax.tick_params(axis='x',rotation=45,labelsize=7); ax.legend(fontsize=8)

for ax in axes:
    ax.text(0.99,0.97,'← 前期',transform=ax.transAxes,ha='right',va='top',fontsize=8,color='#718096')
    ax.text(0.01,0.97,'後期 →',transform=ax.transAxes,ha='left',va='top',fontsize=8,color='#E53E3E')

plt.tight_layout()
fig.savefig('/home/user/AK/ti2_fig_A_trends.png',dpi=150,bbox_inches='tight')
plt.close(); print("Fig A done")

# ── Fig B: 前期/後期比較 + 週次ヒートマップ ──
fig,axes=plt.subplots(1,2,figsize=(18,7),facecolor='#F8F9FA')
fig.suptitle('Phase Comparison & Weekly Heatmap',fontsize=13,fontweight='bold')

# 前期/後期レーダー
ax=axes[0]; ax.remove()
ax_r=fig.add_subplot(1,2,1,projection='polar')
cats=['Morning\nCondition','Sleep\nQuality','Sleep\nHours','Avg RPE\n(inv)','Avg Fatigue\n(inv)']
n=len(cats); angles=[i/n*2*np.pi for i in range(n)]; angles+=angles[:1]

def radar_vals(tr,cd):
    return [
        1-((cd['起床時コンディション'].mean()-1)/4),
        1-((cd['睡眠の質'].mean()-1)/4),
        (cd['睡眠時間'].mean()-5)/4,
        1-((tr['RPE'].mean()-1)/9),
        1-((tr['運動後疲労'].mean()-1)/4),
    ]

v1=radar_vals(tr_e,cd_e)+[radar_vals(tr_e,cd_e)[0]]
v2=radar_vals(tr_l,cd_l)+[radar_vals(tr_l,cd_l)[0]]
ax_r.plot(angles,v1,'o-',lw=2,color=C_B,label=f'前期 (3/30-6/19, n={len(tr_e)}d)')
ax_r.fill(angles,v1,alpha=0.12,color=C_B)
ax_r.plot(angles,v2,'s-',lw=2,color=C_R,label=f'後期 (6/20-7/12, n={len(tr_l)}d)')
ax_r.fill(angles,v2,alpha=0.12,color=C_R)
ax_r.set_thetagrids([a*180/np.pi for a in angles[:-1]],cats,fontsize=9)
ax_r.set_ylim(0,1); ax_r.set_title('前期 vs 後期 比較\n(外側ほど良い)',fontweight='bold',pad=18)
ax_r.legend(loc='upper right',bbox_to_anchor=(1.35,1.2),fontsize=9)

# 週次ヒートマップ
ax=axes[1]; ax.set_facecolor('#F8F9FA')
wk_nums=weekly['wk'].values
mat=np.array([
    (weekly['avg_rpe'].values-1)/9,
    (weekly['avg_fat'].values-1)/4,
    weekly['total_min'].values/weekly['total_min'].max(),
    weekly['days'].values/7,
])
mlabs=['Avg RPE','Avg Fatigue','Vol (norm)','Days/7']
im=ax.imshow(mat,aspect='auto',cmap='RdYlGn_r',vmin=0,vmax=1)
ax.set_xticks(range(len(wk_nums))); ax.set_xticklabels([f'W{w}' for w in wk_nums],fontsize=8)
ax.set_yticks(range(4)); ax.set_yticklabels(mlabs,fontsize=9)
ax.set_title('Weekly Heatmap  (Red=Higher load)',fontweight='bold')
plt.colorbar(im,ax=ax,fraction=0.03,pad=0.04)
raw_vals_list=[weekly['avg_rpe'].values,weekly['avg_fat'].values,weekly['total_min'].values,weekly['days'].values]
for i in range(4):
    for j in range(len(wk_nums)):
        ax.text(j,i,f'{raw_vals_list[i][j]:.1f}',ha='center',va='center',fontsize=7,fontweight='bold')
# Mark phase boundary
split_wk=SPLIT.isocalendar()[1]
for wi,wk in enumerate(wk_nums):
    if wk==split_wk:
        ax.axvline(wi-0.5,color='red',lw=2,ls='--')
        ax.text(wi-0.3,-0.6,'← 前期 | 後期 →',fontsize=8,color='red')

plt.tight_layout()
fig.savefig('/home/user/AK/ti2_fig_B_phase.png',dpi=150,bbox_inches='tight')
plt.close(); print("Fig B done")

# ── Fig C: タンパク質カレンダー（3分割） ──
prot_src=['昼:魚','昼:肉','昼:豆','昼:卵','夕:魚','夕:肉','夕:豆','夕:卵']
prot_raw=['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
          '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']
pc=['#BEE3F8','#FED7D7','#C6F6D5','#FEFCBF','#90CDF4','#FEB2B2','#9AE6B4','#FAF089']
n3=len(df_food)//3
parts=[(0,n3),(n3,2*n3),(2*n3,len(df_food))]
fig,axes=plt.subplots(3,1,figsize=(16,26),facecolor='#F8F9FA')
fig.suptitle('Protein Source Calendar (104 days)',fontsize=13,fontweight='bold')

for part_i,(ax,( s,e)) in enumerate(zip(axes,parts)):
    subset=df_food.iloc[s:e]
    all_cols_h=prot_src+['補食','種類数','水分']
    n_rows,n_cols=len(subset),len(all_cols_h)
    ax.set_xlim(-0.5,n_cols-0.5); ax.set_ylim(-0.5,n_rows-0.5); ax.invert_yaxis()
    ax.set_aspect('equal')
    ax.set_xticks(range(n_cols)); ax.set_xticklabels(all_cols_h,fontsize=8)
    ax.set_yticks(range(n_rows)); ax.set_yticklabels([d.strftime('%m/%d') for d in subset['日付']],fontsize=7)
    ax.xaxis.tick_top(); ax.set_facecolor('#F7FAFC')
    ax.set_title(f'Part {part_i+1}: {subset["日付"].iloc[0].strftime("%m/%d")}–{subset["日付"].iloc[-1].strftime("%m/%d")}',fontweight='bold',pad=20)
    for yi,(_,row) in enumerate(subset.iterrows()):
        tp=0
        for xi,(pr,pcol) in enumerate(zip(prot_raw,pc)):
            has=row[pr]==1
            if has: tp+=1
            rect=plt.Rectangle((xi-0.45,yi-0.45),0.9,0.9,color=pcol if has else 'white',linewidth=0.5,edgecolor='#CCCCCC')
            ax.add_patch(rect)
            if has: ax.text(xi,yi,'●',ha='center',va='center',fontsize=10,color='#2D3748')
        snack=row.get('練習後補食','')
        sc='#C6F6D5' if snack=='はい' else '#FED7D7'
        rect=plt.Rectangle((8-0.45,yi-0.45),0.9,0.9,color=sc,linewidth=0.5,edgecolor='#CCCCCC')
        ax.add_patch(rect)
        ax.text(8,yi,'Y' if snack=='はい' else 'N',ha='center',va='center',fontsize=8,fontweight='bold',
                color='#276749' if snack=='はい' else '#9B2C2C')
        tp_c='#C6F6D5' if tp>=3 else ('#FEFCBF' if tp>=2 else '#FED7D7')
        rect=plt.Rectangle((9-0.45,yi-0.45),0.9,0.9,color=tp_c,linewidth=0.5,edgecolor='#CCCCCC')
        ax.add_patch(rect); ax.text(9,yi,str(tp),ha='center',va='center',fontsize=9,fontweight='bold')
        wm=row.get('水分摂取量_ml',0)
        wm_c='#C6F6D5' if (pd.notna(wm) and wm>=1000) else ('#FEFCBF' if (pd.notna(wm) and wm>=500) else '#FED7D7')
        rect=plt.Rectangle((10-0.45,yi-0.45),0.9,0.9,color=wm_c,linewidth=0.5,edgecolor='#CCCCCC')
        ax.add_patch(rect); ax.text(10,yi,f'{int(wm)/1000:.1f}' if pd.notna(wm) else '',ha='center',va='center',fontsize=7)
        ax.axhline(yi+0.45,color='#E2E8F0',linewidth=0.5)
    ax.axvline(3.5,color='#718096',linewidth=1.5,ls='--')
    ax.axvline(7.5,color='#718096',linewidth=1.5,ls='--')

plt.tight_layout()
fig.savefig('/home/user/AK/ti2_fig_C_protein.png',dpi=120,bbox_inches='tight')
plt.close(); print("Fig C done")

# ── Fig D: 関連性 ──
fig,axes=plt.subplots(1,4,figsize=(18,6),facecolor='#F8F9FA')
fig.suptitle('Behavior vs Performance Analysis',fontsize=13,fontweight='bold')
comps=[
    ('Post-workout\nSupplement\nvs Fatigue',['No Snack','Snack'],[snack_no_fat,snack_yes_fat],[C_GR,C_G],'(Lower=Better)','運動後疲労'),
    ('Water Intake\nvs Fatigue\n(※confounded)',['<1000ml','≥1000ml'],[water_lo,water_hi],[C_B,C_O],'※練習日↔多飲水の交絡','運動後疲労'),
    ('Prev RPE\nvs Next Morn. Cond.',['RPE<7','RPE≥7'],[rpe_lo_cd,rpe_hi_cd],[C_B,C_R],'(Lower=Better Cond)','翌朝CD'),
    ('Sleep Duration\nvs Next-day Fatigue',['<7.5h','≥7.5h'],[sh_lo,sh_hi],[C_O,C_G],'(Lower=Less Fatigue)','翌日疲労'),
]
for ax,(title,labs,vals,cols,sub,ylabel) in zip(axes,comps):
    ax.set_facecolor('#EDF2F4')
    bars=ax.bar(labs,vals,color=cols,alpha=0.85,width=0.5,edgecolor='white',linewidth=1.5)
    for bar,val in zip(bars,vals):
        ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+0.03,f'{val:.2f}',
                ha='center',fontsize=11,fontweight='bold',color='#1A365D')
    diff=vals[1]-vals[0]
    ax.set_title(title,fontweight='bold',fontsize=10)
    ax.set_ylabel(ylabel,fontsize=9); ax.set_ylim(0,max(vals)*1.35)
    ax.text(0.5,0.92,f'diff={diff:+.2f}',transform=ax.transAxes,ha='center',fontsize=9,
            color='#E53E3E' if abs(diff)>=0.3 else C_GR,fontweight='bold')
    ax.text(0.5,0.02,sub,transform=ax.transAxes,ha='center',fontsize=7.5,color='#718096',style='italic')
plt.tight_layout()
fig.savefig('/home/user/AK/ti2_fig_D_corr.png',dpi=150,bbox_inches='tight')
plt.close(); print("Fig D done")

# ── Fig E: 疲労タイムライン ──
fig,ax=plt.subplots(figsize=(16,6),facecolor='#F8F9FA')
ax.set_facecolor('#EDF2F4')
for i,(_,row) in enumerate(df.iterrows()):
    fat=row.get('運動後疲労')
    if pd.notna(fat) and fat>=4:
        ax.axvspan(i-0.5,i+0.5,color='#FED7D7',alpha=0.5,zorder=0)
ax.axvline(list(x_pos)[min(range(len(dates)),key=lambda i:abs(dates.iloc[i]-SPLIT))],
           color='#E53E3E',ls='--',lw=2,label='6/20 phase split')
x_pos2=range(len(df))
ax.plot(x_pos2,[v if (pd.notna(v) and v>1) else np.nan for v in df['運動後疲労']],
        color=C_R,lw=2,marker='o',ms=3,label='Post-workout Fatigue')
ax.plot(x_pos2,[v if pd.notna(v) else np.nan for v in df['起床時コンディション']],
        color=C_G,lw=2,marker='^',ms=3,label='Morning Condition')
ax.plot(x_pos2,[v/2 if (pd.notna(v) and v>1) else np.nan for v in df['RPE']],
        color=C_O,lw=1.5,ls='--',label='RPE÷2')
ax.axhline(4,color=C_R,ls=':',lw=1,alpha=0.4)
ax.axhline(3,color='gray',ls=':',lw=1,alpha=0.3)
ax.set_xticks(list(x_pos2)[::4])
ax.set_xticklabels([dates.iloc[i].strftime('%m/%d') for i in list(x_pos2)[::4]],rotation=45,fontsize=7)
ax.set_ylabel('Score'); ax.set_ylim(0,6)
ax.set_title('Fatigue & Condition Timeline  (Red=fatigue≥4 / Dashed=phase split 6/20)',fontweight='bold')
ax.legend(fontsize=9)
for i,(_,row) in enumerate(df.iterrows()):
    if row.get('きのこ海藻')=='はい':
        ax.plot(i,0.25,marker='*',color='#38A169',ms=5,alpha=0.6)
ax.text(0.01,0.05,'★=きのこ海藻摂取あり',transform=ax.transAxes,fontsize=8,color='#38A169')
plt.tight_layout()
fig.savefig('/home/user/AK/ti2_fig_E_fatigue.png',dpi=150,bbox_inches='tight')
plt.close(); print("Fig E done")

print("All charts done!")

# ── スタイルヘルパー ──
def fill(h): return PatternFill(fill_type='solid',fgColor=h)
def font(bold=False,size=10,color='000000',italic=False):
    return Font(bold=bold,size=size,color=color,name='Arial',italic=italic)
def align(h='center',v='center',wrap=False):
    return Alignment(horizontal=h,vertical=v,wrap_text=wrap)
def thin_border():
    s=Side(style='thin',color='CCCCCC')
    return Border(left=s,right=s,top=s,bottom=s)
def sc(cell,value=None,bg='FFFFFF',bold=False,size=10,h='center',v='center',wrap=False,color='2D3748'):
    if value is not None: cell.value=value
    cell.fill=fill(bg); cell.font=font(bold=bold,size=size,color=color)
    cell.alignment=align(h,v,wrap); cell.border=thin_border()
def sh(cell,text,bg='2E86AB',size=10,color='FFFFFF'):
    cell.value=text; cell.fill=fill(bg)
    cell.font=font(bold=True,size=size,color=color)
    cell.alignment=align(); cell.border=thin_border()

C_H='1A365D'; C_H2='2E86AB'
C_GN='C6F6D5'; C_YL='FEFCBF'; C_OG='FEEBC8'; C_RL='FED7D7'
C_W='FFFFFF'; C_LG='F7FAFC'; C_LG2='EDF2F4'

def cond_col(val):
    if pd.isna(val): return C_W
    if val<=2: return C_GN
    if val==3: return C_YL
    return C_RL

def rpe_col(val):
    if pd.isna(val) or val<=1: return C_LG
    if val<=5: return C_GN
    if val<=7: return C_YL
    return C_OG if val<=8 else C_RL

# ── ワークブック ──
wb2=openpyxl.Workbook(); wb2.remove(wb2.active)

# ── はじめに ──
ws0=wb2.create_sheet('はじめに',0); ws0.sheet_view.showGridLines=False
ws0.column_dimensions['A'].width=2; ws0.column_dimensions['B'].width=90
ws0.row_dimensions[1].height=50
c=ws0['B1']; c.value='TI選手 フィードバックシート  2026.03.30 – 2026.07.12'
c.fill=fill(C_H); c.font=font(bold=True,size=18,color='FFFFFF'); c.alignment=align('left','center')
entries=[('■ シート構成',''),('① サマリー','主要KPI・前期/後期比較・コーチ記入欄・選手振り返りQ&A'),
         ('② 日次統合データ','全104日を1行に統合。色分けで状態が一目でわかる'),
         ('③ 食事バランス','タンパク源カレンダー（3分割）＋水分・きのこ海藻'),
         ('④ トレンドグラフ','体重・コンディション・RPE・疲労・睡眠・前後期比較'),
         ('⑤ 関連性ヒント','4つの行動vs成果の比較分析'),('',''),
         ('■ スコアの読み方（重要）',''),
         ('起床時コンディション (1〜5)','1=とても良い  5=とても悪い  ※数値が小さいほど良好'),
         ('睡眠の質 (1〜5)','1=よく眠れた  5=全然眠れなかった  ※数値が小さいほど良好'),
         ('運動後疲労 (1〜5)','1=疲労なし  5=非常に疲れた  ※数値が小さいほど良好'),
         ('RPE (1〜10)','1=ほぼ安静  10=最大努力。6〜7=中強度、8以上=高強度')]
for r,(title,body) in enumerate(entries,2):
    ws0.row_dimensions[r].height=20 if title else 10
    if not title and not body: continue
    txt=f'  {title}  →  {body}' if body else title
    c=ws0.cell(row=r,column=2,value=txt)
    c.fill=fill('34495E' if title.startswith('■') else (C_LG2 if r%2==0 else C_W))
    c.font=font(bold=True,size=11 if title.startswith('■') else 10,
                color='FFFFFF' if title.startswith('■') else '2D3748')
    c.alignment=align('left','center')
    if body: c.border=thin_border()

# ── ① サマリー ──
ws1=wb2.create_sheet('① サマリー'); ws1.sheet_view.showGridLines=False
for col,w in {'A':2,'B':34,'C':16,'D':20,'E':44}.items(): ws1.column_dimensions[col].width=w

ws1.merge_cells('B1:E1')
c=ws1['B1']; c.value='TI選手 フィードバックレポート'
c.fill=fill(C_H); c.font=font(bold=True,size=16,color='FFFFFF')
c.alignment=align('left','center'); ws1.row_dimensions[1].height=36
ws1.merge_cells('B2:C2'); ws1['B2'].value='対象期間: 2026.03.30 – 2026.07.12'
ws1['B2'].fill=fill('2B6CB0'); ws1['B2'].font=font(size=10,color='FFFFFF'); ws1['B2'].alignment=align('left','center')
ws1.merge_cells('D2:E2'); ws1['D2'].value='レポート作成日: 2026.07.12'
ws1['D2'].fill=fill('2B6CB0'); ws1['D2'].font=font(size=10,color='FFFFFF'); ws1['D2'].alignment=align('right','center')
ws1.row_dimensions[2].height=20; ws1.row_dimensions[3].height=8

ws1.merge_cells('B4:E4')
c=ws1['B4']; c.value='■ 期間サマリー（104日間）'
c.fill=fill(C_H2); c.font=font(bold=True,size=11,color='FFFFFF')
c.alignment=align('left','center'); ws1.row_dimensions[4].height=24

for ci,h in enumerate(['指標','今期間','評価目安','備考'],2):
    sh(ws1.cell(row=5,column=ci),h,bg='34495E',size=10)
ws1.row_dimensions[5].height=20

kpi_rows=[
    ('総トレーニング日数（休養除く）',f'{total_train} 日','休養日とのバランスを確認',
     f'休養日 {total_rest} 日 ／ 計 {total_train+total_rest} 日（104日間）'),
    ('総トレーニング時間（分）',f'{total_min:,} 分','前週との比較で過負荷を確認','急激な増加は怪我リスク'),
    ('平均RPE（練習日のみ）',f'{avg_rpe:.1f}','6〜7が中強度の目安','高い日が続く時は回復を意識'),
    ('平均運動後疲労（練習日のみ）',f'{avg_fat:.1f} / 5','低いほど回復良好','4以上が続く場合は疲労蓄積のサイン'),
    ('平均睡眠時間 (h)',f'{avg_sleep_h:.1f} h','7時間以上が目安','8時間以上が理想'),
    ('平均睡眠の質（1=良/5=悪）',f'{avg_sleep_q:.1f}','2以下が望ましい','就寝前ルーティン見直しを'),
    ('平均起床時コンディション（1=良/5=悪）',f'{avg_cd:.1f}','2以下が望ましい','主観の悪化は早期疲労サイン'),
    ('平均体重（kg）',f'{avg_wt:.1f} kg','±1kg以内が目安',
     f'期初 {wt_first:.1f} kg → 期末 {wt_last:.1f} kg（{wt_last-wt_first:+.1f} kg）'),
    ('体重変動幅（kg）',f'{wt_range:.1f} kg','1.5kg以内が目安','大きい場合は水分・食事量を確認'),
    ('練習後補食「はい」の日数',f'{snack_yes} 日 / {n_total} 日','練習日は毎回が理想',
     f'実施率 {snack_yes/n_total*100:.0f}%'),
    ('水分摂取1000ml以上の日数',f'{water_1000} 日 / {n_total} 日','毎日1000ml以上が目安',
     f'実施率 {water_1000/n_total*100:.0f}% — 前期（68/81日）から大幅改善！'),
    ('きのこ・海藻「はい」の日数',f'{kino_yes} 日 / {n_total} 日','週4日以上が目安',
     f'実施率 {kino_yes/n_total*100:.0f}%。ミネラル・食物繊維の継続的な補給ができています'),
    ('タンパク源の平均種類数/日',f'{avg_protein:.1f} 種類','2種類以上が目安',
     '昼食のタンパク源をさらに強化すると回復力アップが期待できます'),
]
for ri,(ind,val,target,note) in enumerate(kpi_rows,6):
    ws1.row_dimensions[ri].height=22
    bg=C_LG if ri%2==0 else C_W
    for ci,txt in enumerate([ind,val,target,note],2):
        c=ws1.cell(row=ri,column=ci,value=txt)
        c.fill=fill(bg); c.font=font(size=10,color='2D3748',bold=(ci==2))
        c.alignment=align('left' if ci in [2,4,5] else 'center','center',wrap=(ci==5))
        c.border=thin_border()
    ws1.cell(row=ri,column=3).font=font(bold=True,size=11,color='1A365D')
    ws1.cell(row=ri,column=3).alignment=align('center','center')

# 前期/後期比較ボックス
r=20; ws1.row_dimensions[r].height=10
r+=1; ws1.row_dimensions[r].height=24
ws1.merge_cells(f'B{r}:E{r}')
c=ws1[f'B{r}']; c.value='■ 前期 vs 後期 比較（6/20を境に）'
c.fill=fill(C_H2); c.font=font(bold=True,size=11,color='FFFFFF'); c.alignment=align('left','center')
r+=1; ws1.row_dimensions[r].height=20
for ci,h in enumerate(['指標','前期 (3/30-6/19)','後期 (6/20-7/12)','変化'],2):
    sh(ws1.cell(row=r,column=ci),h,bg='34495E',size=10)
phase_rows=[
    ('練習日数',f'{len(tr_e)} 日',f'{len(tr_l)} 日','—'),
    ('平均RPE',f'{tr_e["RPE"].mean():.2f}',f'{tr_l["RPE"].mean():.2f}',
     f'{tr_l["RPE"].mean()-tr_e["RPE"].mean():+.2f}'),
    ('平均運動後疲労',f'{tr_e["運動後疲労"].mean():.2f}',f'{tr_l["運動後疲労"].mean():.2f}',
     f'{tr_l["運動後疲労"].mean()-tr_e["運動後疲労"].mean():+.2f} (↓改善)' if tr_l["運動後疲労"].mean()<tr_e["運動後疲労"].mean() else f'{tr_l["運動後疲労"].mean()-tr_e["運動後疲労"].mean():+.2f}'),
    ('平均起床時コンディション',f'{cd_e["起床時コンディション"].mean():.2f}',f'{cd_l["起床時コンディション"].mean():.2f}',
     f'{cd_l["起床時コンディション"].mean()-cd_e["起床時コンディション"].mean():+.2f} (↓改善)' if cd_l["起床時コンディション"].mean()<cd_e["起床時コンディション"].mean() else f'{cd_l["起床時コンディション"].mean()-cd_e["起床時コンディション"].mean():+.2f}'),
    ('平均睡眠の質',f'{cd_e["睡眠の質"].mean():.2f}',f'{cd_l["睡眠の質"].mean():.2f}',
     f'{cd_l["睡眠の質"].mean()-cd_e["睡眠の質"].mean():+.2f}'),
]
for pr_i,(pind,pval1,pval2,pchg) in enumerate(phase_rows,r+1):
    ws1.row_dimensions[pr_i].height=20
    pbg=C_LG if pr_i%2==0 else C_W
    for ci,txt in enumerate([pind,pval1,pval2,pchg],2):
        c=ws1.cell(row=pr_i,column=ci,value=txt)
        bg_cell=C_GN if ('改善' in str(pchg) and ci==5) else pbg
        sc(c,bg=bg_cell,size=10,h='center' if ci>2 else 'left',color='276749' if '改善' in str(pchg) and ci==5 else '2D3748')
r=pr_i+2; ws1.row_dimensions[r].height=10

ws1.merge_cells(f'B{r}:E{r}')
c=ws1[f'B{r}']; c.value='■ 今期間のハイライト（コーチ記入欄）'
c.fill=fill(C_H2); c.font=font(bold=True,size=11,color='FFFFFF')
c.alignment=align('left','center'); ws1.row_dimensions[r].height=24

comments=[
    ('① よかった点（継続したい行動）',
     f'◯ 水分摂取が{water_1000}日/{n_total}日（{water_1000/n_total*100:.0f}%）と前期から大幅に改善しました！暑熱期に入り、意識的に水分補給を強化できている証拠です。この習慣を継続してください。\n'
     f'◯ きのこ・海藻の摂取も{kino_yes}日（{kino_yes/n_total*100:.0f}%）と高水準を維持しています。\n'
     f'◯ 後期（6/20〜）の平均運動後疲労が{tr_l["運動後疲労"].mean():.2f}と前期({tr_e["運動後疲労"].mean():.2f})より改善。暑熱環境への適応が始まっています。',
     C_GN),
    ('② 気になった点（早めに手を打ちたいこと）',
     f'◯ 7/8のメモに「暑すぎてダウンした」とあります。気温が高い時間帯の練習は熱中症リスクが高いため、早朝・夕方への練習時間帯の変更、またはインターバル（練習中の休憩）の挿入を検討してください。\n'
     f'◯ 平均運動後疲労が{avg_fat:.2f}/5と依然高め。週に最低1日の完全休養を確保し、疲労の「リセット日」を意識的に作ることを強くお勧めします（現在 休養日{total_rest}日/{total_train+total_rest}日）。\n'
     f'◯ 睡眠の質（平均{avg_sleep_q:.1f}）がまだ改善の余地あり。暑熱期は体温が下がりにくく睡眠の質が低下しやすいため、就寝前の入浴（シャワーでもOK）や室温管理（26℃以下）を意識してください。',
     C_OG),
    ('③ 次の大会までの小さな目標（1つだけ）',
     f'◯ 暑い日は練習開始前・中・後に各500ml（計1500ml以上）を意識して飲む。\n'
     f'　 理由: 7月の気温上昇により発汗量が増加し、従来の1000ml目標では不十分になっています。体重測定（練習前後）で水分損失を確認する習慣もつけてみましょう。',
     C_YL),
]
for title,body,bg_c in comments:
    r+=1; ws1.row_dimensions[r].height=18
    ws1.merge_cells(f'B{r}:E{r}')
    c=ws1[f'B{r}']; c.value=title
    c.fill=fill('34495E'); c.font=font(bold=True,size=10,color='FFFFFF'); c.alignment=align('left','center')
    r+=1; ws1.row_dimensions[r].height=80
    ws1.merge_cells(f'B{r}:E{r}')
    c=ws1[f'B{r}']; c.value=body
    c.fill=fill(bg_c); c.font=font(size=10,color='2D3748')
    c.alignment=align('left','top',wrap=True); c.border=thin_border()

ws1.row_dimensions[r+1].height=10; r+=2
ws1.merge_cells(f'B{r}:E{r}')
c=ws1[f'B{r}']; c.value='■ 選手から（自己振り返り欄）'
c.fill=fill(C_H2); c.font=font(bold=True,size=11,color='FFFFFF')
c.alignment=align('left','center'); ws1.row_dimensions[r].height=24
for q in ['Q1. 今期間で「調子がよかった」と感じた日と、その理由',
          'Q2. 逆に「うまくいかなかった」日と、思い当たる原因',
          'Q3. 次に試してみたいこと（食事・睡眠・練習どれか1つ）']:
    r+=1; ws1.row_dimensions[r].height=18
    ws1.merge_cells(f'B{r}:E{r}')
    c=ws1[f'B{r}']; c.value=q
    c.fill=fill('34495E'); c.font=font(bold=True,size=10,color='FFFFFF'); c.alignment=align('left','center')
    r+=1; ws1.row_dimensions[r].height=50
    ws1.merge_cells(f'B{r}:E{r}')
    c=ws1[f'B{r}']; c.value='（選手記入欄）'
    c.fill=fill('F0F8FF'); c.font=font(size=10,color='A0AEC0',italic=True)
    c.alignment=align('left','top',wrap=True); c.border=thin_border()

print("Sheet ① done")

# ── ② 日次統合データ ──
ws2=wb2.create_sheet('② 日次統合データ'); ws2.sheet_view.showGridLines=False
for col,w in {'A':2,'B':11,'C':16,'D':8,'E':7,'F':8,'G':8,'H':8,'I':9,'J':9,'K':9,'L':9,'M':7,'N':10,'O':8,'P':8}.items():
    ws2.column_dimensions[col].width=w
ws2.merge_cells('B1:P1')
c=ws2['B1']; c.value='日次統合データ（全104日）'
c.fill=fill(C_H); c.font=font(bold=True,size=14,color='FFFFFF')
c.alignment=align('left','center'); ws2.row_dimensions[1].height=30
ws2.merge_cells('B2:P2')
c=ws2['B2']; c.value='緑=良好 / 黄=普通 / 橙・赤=要注意　（起床CD・睡眠の質・疲労は数値が小さいほど良い）'
c.fill=fill('EBF8FF'); c.font=font(size=9,color='2B6CB0'); c.alignment=align('left','center')
ws2.row_dimensions[2].height=18; ws2.row_dimensions[3].height=8

hdrs2=['日付','種目','時間(分)','RPE','爆発力','持久力','運動後疲労','体重(kg)',
       '起床CD','睡眠の質','睡眠時間','補食','栄養Bal','水分(ml)','きのこ','タンパク数']
for ci,h in enumerate(hdrs2,2): sh(ws2.cell(row=4,column=ci),h,bg=C_H2,size=9)
ws2.row_dimensions[4].height=22

for ri,(_,row) in enumerate(df.iterrows(),5):
    ws2.row_dimensions[ri].height=18
    kind=str(row.get('種目','')) if pd.notna(row.get('種目')) else ''
    is_rest='休養' in kind
    rbg='F7FAFC' if is_rest else (C_LG if ri%2==0 else C_W)
    # Phase marker
    if row['日付']==SPLIT: ws2.row_dimensions[ri].height=24

    sc(ws2.cell(row=ri,column=2),row['日付'].strftime('%m/%d'),bg=('FFFDE7' if row['日付']>=SPLIT else rbg),bold=True,size=9)
    sc(ws2.cell(row=ri,column=3),kind.replace('実践トレーニング','実践').replace('休養日','休養').replace('ウエイトトレーニング','WT'),bg=rbg,h='left',size=9)
    sc(ws2.cell(row=ri,column=4),int(row['時間_分']) if pd.notna(row.get('時間_分')) and row['時間_分']>0 else '',bg=rbg,size=9)
    rpe=row.get('RPE')
    sc(ws2.cell(row=ri,column=5),int(rpe) if pd.notna(rpe) and rpe>1 else '',bg=rpe_col(rpe) if not is_rest else rbg,size=9)
    for ci_off,cn in enumerate(['爆発力','持久力'],6):
        v=row.get(cn); sc(ws2.cell(row=ri,column=ci_off),int(v) if pd.notna(v) and v>1 else '',bg=rbg,size=9)
    fat=row.get('運動後疲労')
    sc(ws2.cell(row=ri,column=8),int(fat) if pd.notna(fat) and fat>1 else '',
       bg=cond_col(fat) if (pd.notna(fat) and fat>1) else rbg,bold=(pd.notna(fat) and fat>=4),size=9)
    wt=row.get('体重_kg'); sc(ws2.cell(row=ri,column=9),float(wt) if pd.notna(wt) else '',bg=rbg,size=9)
    cd=row.get('起床時コンディション'); sc(ws2.cell(row=ri,column=10),int(cd) if pd.notna(cd) else '',bg=cond_col(cd) if pd.notna(cd) else rbg,size=9)
    sq=row.get('睡眠の質'); sc(ws2.cell(row=ri,column=11),int(sq) if pd.notna(sq) else '',bg=cond_col(sq) if pd.notna(sq) else rbg,size=9)
    sh_=row.get('睡眠時間')
    sh_bg=C_GN if (pd.notna(sh_) and sh_>=8) else (C_YL if (pd.notna(sh_) and sh_>=7) else rbg)
    sc(ws2.cell(row=ri,column=12),float(sh_) if pd.notna(sh_) else '',bg=sh_bg,size=9)
    snack=row.get('練習後補食','')
    sc(ws2.cell(row=ri,column=13),str(snack) if pd.notna(snack) else '',
       bg=C_GN if snack=='はい' else (C_RL if snack=='いいえ' else rbg),size=9,
       color='276749' if snack=='はい' else ('9B2C2C' if snack=='いいえ' else '2D3748'))
    nb=row.get('栄養バランス'); sc(ws2.cell(row=ri,column=14),int(nb) if pd.notna(nb) else '',bg=cond_col(nb) if pd.notna(nb) else rbg,size=9)
    wm=row.get('水分摂取量_ml')
    wm_bg=C_GN if (pd.notna(wm) and wm>=1000) else (C_YL if (pd.notna(wm) and wm>=500) else C_RL)
    sc(ws2.cell(row=ri,column=15),int(wm) if pd.notna(wm) else '',bg=wm_bg,size=9)
    kino=row.get('きのこ海藻','')
    sc(ws2.cell(row=ri,column=16),'★' if kino=='はい' else '',bg=C_GN if kino=='はい' else rbg,size=9,color='276749' if kino=='はい' else '2D3748')
    tp=row.get('タンパク質摂取数')
    tp_bg=C_GN if (pd.notna(tp) and tp>=3) else (C_YL if (pd.notna(tp) and tp>=2) else rbg)
    sc(ws2.cell(row=ri,column=17),int(tp) if pd.notna(tp) else '',bg=tp_bg,size=9)

# 平均行
ar=len(df)+5; ws2.row_dimensions[ar].height=22
sc(ws2.cell(row=ar,column=2,value='平均/合計'),bg='34495E',bold=True,size=9,color='FFFFFF')
for ci,val in {4:int(df['時間_分'].fillna(0).sum()),5:round(train_only['RPE'].mean(),1),
               6:round(train_only['爆発力'].mean(),1),7:round(train_only['持久力'].mean(),1),
               8:round(train_only['運動後疲労'].mean(),1),9:round(df_body['体重_kg'].mean(),1),
               10:round(df_cond['起床時コンディション'].mean(),1),11:round(df_cond['睡眠の質'].mean(),1),
               12:round(df_cond['睡眠時間'].mean(),1)}.items():
    sc(ws2.cell(row=ar,column=ci,value=val),bg=C_LG2,bold=True,size=9,color='1A365D')
sc(ws2.cell(row=ar,column=13,value=f'{snack_yes}回'),bg=C_GN,bold=True,size=9,color='276749')
sc(ws2.cell(row=ar,column=15,value=f'{water_1000}日'),bg=C_GN,bold=True,size=9)
sc(ws2.cell(row=ar,column=16,value=f'{kino_yes}日'),bg=C_GN,bold=True,size=9)
sc(ws2.cell(row=ar,column=17,value=round(df_food['タンパク質摂取数'].mean(),1)),bg=C_LG2,bold=True,size=9)
print("Sheet ② done")

# ── ③ 食事バランス ──
ws3=wb2.create_sheet('③ 食事バランス'); ws3.sheet_view.showGridLines=False
ws3.column_dimensions['A'].width=2; ws3.column_dimensions['B'].width=10
for cl in list('CDEFGHIJKL')+['M','N','O']: ws3.column_dimensions[cl].width=7
ws3.merge_cells('B1:O1')
c=ws3['B1']; c.value='タンパク源バランス＋水分・きのこ海藻 (104日間・3分割)'
c.fill=fill(C_H); c.font=font(bold=True,size=13,color='FFFFFF'); c.alignment=align('left','center'); ws3.row_dimensions[1].height=28
ws3.merge_cells('B2:O2')
c=ws3['B2']; c.value='◎「魚・肉・豆・卵」がバランスよく揃うと回復が早まります。水分・きのこ海藻も色で確認できます。'
c.fill=fill('F0FFF4'); c.font=font(size=9,color='276749'); c.alignment=align('left','center'); ws3.row_dimensions[2].height=18

prot_raw_all=['昼タンパク質_魚','昼タンパク質_肉','昼タンパク質_豆','昼タンパク質_卵',
              '夕タンパク質_魚','夕タンパク質_肉','夕タンパク質_豆','夕タンパク質_卵']
pc_all=['BEE3F8','FED7D7','C6F6D5','FEFCBF','90CDF4','FEB2B2','9AE6B4','FAF089']
all_hdr=['日付','昼:魚','昼:肉','昼:豆','昼:卵','夕:魚','夕:肉','夕:豆','夕:卵','種類数','補食','水分(L)','きのこ']
hdr_bgs=['2E86AB','BEE3F8','FED7D7','C6F6D5','FEFCBF','90CDF4','FEB2B2','9AE6B4','FAF089','2E86AB','2E86AB','BEE3F8','C6F6D5']
hdr_fgs=['FFFFFF','1A365D','1A365D','1A365D','1A365D','1A365D','1A365D','1A365D','1A365D','FFFFFF','FFFFFF','1A365D','1A365D']

# Section headers
n3_=len(df_food)//3
section_starts=[5,5+n3_+2,5+2*n3_+4]
current_r=3
for part_i in range(3):
    s_=part_i*n3_; e_=min((part_i+1)*n3_,len(df_food))
    subset=df_food.iloc[s_:e_]
    ws3.merge_cells(f'B{current_r}:O{current_r}')
    c=ws3[f'B{current_r}']
    c.value=f'Part {part_i+1}: {subset["日付"].iloc[0].strftime("%Y/%m/%d")} – {subset["日付"].iloc[-1].strftime("%Y/%m/%d")}'
    c.fill=fill('34495E'); c.font=font(bold=True,size=10,color='FFFFFF'); c.alignment=align('left','center')
    ws3.row_dimensions[current_r].height=18; current_r+=1
    ws3.merge_cells(f'C{current_r}:F{current_r}')
    c=ws3[f'C{current_r}']; c.value='── 昼 食 ──'; c.fill=fill('BEE3F8'); c.font=font(bold=True,size=9,color='2C5282'); c.alignment=align()
    ws3.merge_cells(f'G{current_r}:J{current_r}')
    c=ws3[f'G{current_r}']; c.value='── 夕 食 ──'; c.fill=fill('FEB2B2'); c.font=font(bold=True,size=9,color='742A2A'); c.alignment=align()
    ws3.row_dimensions[current_r].height=16; current_r+=1
    for ci,(h,bg,fg) in enumerate(zip(all_hdr,hdr_bgs,hdr_fgs),2):
        sh(ws3.cell(row=current_r,column=ci),h,bg=bg,size=9,color=fg)
    ws3.row_dimensions[current_r].height=20; current_r+=1
    for _,row in subset.iterrows():
        ws3.row_dimensions[current_r].height=17
        rbg=C_W if current_r%2==0 else C_LG
        sc(ws3.cell(row=current_r,column=2),row['日付'].strftime('%m/%d'),bg=rbg,bold=True,size=9)
        tp_=0
        for xi,(pr,pcol) in enumerate(zip(prot_raw_all,pc_all),3):
            has=row[pr]==1
            if has: tp_+=1
            c=ws3.cell(row=current_r,column=xi)
            c.value='●' if has else ''; c.fill=fill(pcol if has else rbg)
            c.font=font(bold=True,size=11,color='1A365D' if has else 'CCCCCC')
            c.alignment=align(); c.border=thin_border()
        tp_bg=C_GN if tp_>=3 else (C_YL if tp_>=2 else (C_RL if tp_==0 else C_OG))
        sc(ws3.cell(row=current_r,column=11),tp_,bg=tp_bg,bold=True,size=10)
        snack=row.get('練習後補食','')
        sc(ws3.cell(row=current_r,column=12),'Y' if snack=='はい' else 'N',
           bg=C_GN if snack=='はい' else C_RL,size=9,
           color='276749' if snack=='はい' else '9B2C2C',bold=(snack=='はい'))
        wm=row.get('水分摂取量_ml')
        wm_bg=C_GN if (pd.notna(wm) and wm>=1000) else (C_YL if (pd.notna(wm) and wm>=500) else C_RL)
        sc(ws3.cell(row=current_r,column=13),f'{int(wm)/1000:.1f}L' if pd.notna(wm) else '',bg=wm_bg,size=9)
        kino=row.get('きのこ海藻','')
        sc(ws3.cell(row=current_r,column=14),'★' if kino=='はい' else '',bg=C_GN if kino=='はい' else rbg,size=9,color='276749')
        current_r+=1
    # 集計行
    ws3.row_dimensions[current_r].height=20
    sc(ws3.cell(row=current_r,column=2),value='摂取日数',bg='34495E',bold=True,size=9,color='FFFFFF')
    for xi,pr in enumerate(prot_raw_all,3):
        cnt=int(subset[pr].sum())
        sc(ws3.cell(row=current_r,column=xi),cnt,bg=C_GN if cnt>=n3_//2 else (C_YL if cnt>=n3_//4 else C_RL),bold=True,size=10)
    sc(ws3.cell(row=current_r,column=11),round(subset['タンパク質摂取数'].mean(),1),bg=C_GN,bold=True,size=10)
    sc(ws3.cell(row=current_r,column=12),f'{int(subset["補食_bin"].sum())}日',bg=C_GN,bold=True,size=10)
    sc(ws3.cell(row=current_r,column=13),f'{int((subset["水分摂取量_ml"]>=1000).sum())}日',bg=C_GN,bold=True,size=10)
    sc(ws3.cell(row=current_r,column=14),f'{int((subset["きのこ海藻"]=="はい").sum())}日',bg=C_GN,bold=True,size=10)
    current_r+=2

print("Sheet ③ done")

# ── ④ トレンドグラフ ──
ws4=wb2.create_sheet('④ トレンドグラフ'); ws4.sheet_view.showGridLines=False
ws4.column_dimensions['A'].width=2
ws4.merge_cells('B1:J1')
c=ws4['B1']; c.value='トレンドグラフ（2026.03.30 – 2026.07.12）'
c.fill=fill(C_H); c.font=font(bold=True,size=14,color='FFFFFF')
c.alignment=align('left','center'); ws4.row_dimensions[1].height=30
ws4.merge_cells('B2:J2')
c=ws4['B2']; c.value='赤点線は6/20（前期/後期の境界）。104日間のデータを可視化しています。'
c.fill=fill('EBF8FF'); c.font=font(size=9,color='2B6CB0'); c.alignment=align('left','center'); ws4.row_dimensions[2].height=18
try:
    for fname,rs in [('ti2_fig_A_trends.png',4),('ti2_fig_B_phase.png',38),('ti2_fig_E_fatigue.png',62)]:
        img=XLImage(f'/home/user/AK/{fname}'); img.width=900; img.height=450
        ws4.add_image(img,f'B{rs}')
    print("Charts embedded OK")
except Exception as e: print(f"warn:{e}")

# ── ⑤ 関連性ヒント ──
ws5=wb2.create_sheet('⑤ 関連性ヒント'); ws5.sheet_view.showGridLines=False
for col,w in {'A':2,'B':30,'C':20,'D':13,'E':20,'F':13,'G':13,'H':42}.items(): ws5.column_dimensions[col].width=w
ws5.merge_cells('B1:H1')
c=ws5['B1']; c.value='行動とパフォーマンスの関連性（TI選手 専用分析 / 104日間）'
c.fill=fill(C_H); c.font=font(bold=True,size=14,color='FFFFFF')
c.alignment=align('left','center'); ws5.row_dimensions[1].height=30
ws5.merge_cells('B2:H2')
c=ws5['B2']
c.value='104日間のデータに基づきます。データ量が増えたことで傾向の信頼性が高まっています。差の絶対値0.3以上が注目の目安。'
c.fill=fill('FFFAF0'); c.font=font(size=9,color='744210'); c.alignment=align('left','center',wrap=True); ws5.row_dimensions[2].height=26
ws5.row_dimensions[3].height=8
for ci,h in enumerate(['観点','A群条件','A群平均','B群条件','B群平均','差(B-A)','解釈'],2):
    sh(ws5.cell(row=4,column=ci),h,bg=C_H2,size=10)
ws5.row_dimensions[4].height=22

rel_rows=[
    ('練習後補食 → 当日の運動後疲労','補食「いいえ」',round(snack_no_fat,2),'補食「はい」',round(snack_yes_fat,2),
     round(snack_yes_fat-snack_no_fat,2),
     f'差は{abs(snack_yes_fat-snack_no_fat):.2f}と小さい（104日間でも傾向が見られない）。補食の「タイミング・内容（タンパク質量）」を記録すると次のステップの分析ができます。'),
    ('水分摂取量 → 当日の運動後疲労\n(※交絡注意)','水分<1000ml',round(water_lo,2),'水分≥1000ml',round(water_hi,2),
     round(water_hi-water_lo,2),
     f'水分が多い日に疲労が高いのは「ハードな練習日ほど多く飲む」という交絡が原因。7月の暑熱期は平常時より+500ml増量を推奨します。'),
    ('前日RPE → 翌朝の起床時コンディション','前日RPE<7',round(rpe_lo_cd,2),'前日RPE≥7',round(rpe_hi_cd,2),
     round(rpe_hi_cd-rpe_lo_cd,2),
     f'高RPE翌朝のコンディションが良いのは「調子の良い日に高強度練習する」という逆の因果関係が影響している可能性あり。高RPE日の前日夜の行動（補食・睡眠時間）を振り返ってみましょう。'),
    ('睡眠時間7.5h以上 → 翌日の運動後疲労','睡眠<7.5h',round(sh_lo,2),'睡眠≥7.5h',round(sh_hi,2),
     round(sh_hi-sh_lo,2),
     f'睡眠時間と翌日疲労の関連はほぼゼロ（104日間）。睡眠の「量」より「質」改善が有効かもしれません。現在の平均睡眠の質スコア：{avg_sleep_q:.1f}/5。'),
]
for ri,(obs,ac,av,bc,bv,diff,interp) in enumerate(rel_rows,5):
    ws5.row_dimensions[ri].height=58
    rbg=C_LG if ri%2==0 else C_W
    sc(ws5.cell(row=ri,column=2,value=obs),bg=rbg,bold=True,h='left',wrap=True,size=10)
    sc(ws5.cell(row=ri,column=3,value=ac),bg=C_RL,h='center',size=9)
    sc(ws5.cell(row=ri,column=4,value=av),bg=C_RL,bold=True,size=11,color='9B2C2C')
    sc(ws5.cell(row=ri,column=5,value=bc),bg=C_GN,h='center',size=9)
    sc(ws5.cell(row=ri,column=6,value=bv),bg=C_GN,bold=True,size=11,color='276749')
    diff_bg=C_GN if diff<-0.3 else (C_YL if abs(diff)<0.3 else C_OG)
    sc(ws5.cell(row=ri,column=7,value=f'{diff:+.2f}'),bg=diff_bg,bold=True,size=11)
    sc(ws5.cell(row=ri,column=8,value=interp),bg=rbg,h='left',wrap=True,size=9)

try:
    img=XLImage('/home/user/AK/ti2_fig_D_corr.png'); img.width=920; img.height=440
    ws5.add_image(img,'B10'); print("Corr chart OK")
except Exception as e: print(f"warn:{e}")

# ── 保存 ──
out='/home/user/AK/TI_athlete_feedback_report_v2.xlsx'
wb2.save(out)
print(f'\nSaved: {out}')
