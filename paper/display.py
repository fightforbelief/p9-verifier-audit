"""Typeset the returned study reports. Run from paper/ after both archives finish."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

ROOT=Path(__file__).resolve().parent
REPORTS=ROOT.parent/"reports"
names={"gsm8k":"GSM8K","math500":"MATH-500","minerva_math":"Minerva Math",
       "gaokao2023en":"Gaokao","olympiadbench":"OlympiadBench","college_math":"College Math",
       "mmlu_stem":"MMLU STEM","lightman":"Lightman (MATH)"}


def main():
    subjects={k:json.loads((REPORTS/f"{k}.json").read_text()) for k in names
              if (REPORTS/f"{k}.json").is_file()}
    rows=[]
    checks=[]
    for k,rep in subjects.items():
        x=rep["results"]["8"]
        a,c=x["answer"],x["candidate"]
        policy=a["policies"]
        rows.append(" & ".join([names[k],f"{rep['problems']:,}",f"{a['units']:,}",f"{100*a['gap']:+.2f}",
                    f"{c['policies']['difference']['sign']['0']:,}",f"{policy['pooled']['sign']['0']:,}",
                    f"{policy['difference']['sign']['0']:,}",str(a["erase"])])+r" \\")
        cs=[]
        for n,v in rep['results'].items():
            ans=v['answer']
            cs.append((100*ans['gap'],ans['policies']['difference']['sign']['0'],ans['erase']))
        checks.append(" & ".join([names[k],*[f"{t[0]:+.2f}" for t in cs],
                                  *[f"{t[1]:,}" for t in cs],*[str(t[2]) for t in cs]])+r" \\")
    (ROOT/"at_eight.tex").write_text("\n".join(rows)+"\n")
    (ROOT/"scaling.tex").write_text("\n".join(checks)+"\n")
    # Ratios use the same number of reviewed answers for both orderings.
    fig,ax=plt.subplots(figsize=(6.8,3.1))
    y=list(range(len(subjects)))
    styles=[("difference","Mass difference","o","#14615d"),("pooled","Pooled winner mass","s","#996029"),
            ("random","Uniform (expected)","x","#575e73")]
    for mode,label,marker,color in styles:
        vals=[]
        for rep in subjects.values():
            a=rep["results"]["8"]["answer"]
            width=a['random_width10'] if mode=='random' else a['policies'][mode]['width10']
            vals.append(width/a['initial_width'])
        ax.scatter(vals,y,label=label,marker=marker,s=31,color=color,zorder=3)
    ax.set_yticks(y,list(names[k] for k in subjects))
    ax.invert_yaxis()
    ax.set_xlim(-.025,1.015)
    ax.xaxis.set_major_formatter(PercentFormatter(xmax=1,decimals=0))
    ax.set_xlabel("Fraction of initial uncertainty width remaining")
    ax.grid(axis='x',lw=.5,alpha=.4)
    ax.spines[['right','top','left']].set_visible(False)
    ax.tick_params(axis='y',length=0)
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.0),ncol=3,frameon=False,fontsize=8.5)
    fig.tight_layout()
    fig.savefig(ROOT/"widths.pdf",metadata={"CreationDate":None,"ModDate":None})
    plt.close(fig)


if __name__=="__main__":
    main()
