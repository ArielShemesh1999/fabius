"""Minimal numpy->SVG line-plotter for fabius research figures. Stdlib + numpy only.

Renders clean, GitHub-friendly line plots (light card, dark ink, blue/green accents).
Used by render_figures.py to produce the conceptual decision-model diagrams in RESEARCH.md.
The figures are ILLUSTRATIVE shapes of documented principles, not fabius measurements.
"""
import numpy as np

W, H = 660, 410
ML, MR, MT, MB = 74, 26, 48, 60           # margins
PX, PY = W-ML-MR, H-MT-MB                  # plot area

def _sx(x, xlim): return ML + (x-xlim[0])/(xlim[1]-xlim[0])*PX
def _sy(y, ylim): return MT + (1-(y-ylim[0])/(ylim[1]-ylim[0]))*PY

def plot(path, title, xlabel, ylabel, series, xlim, ylim,
         xticks=None, yticks=None, vlines=None, points=None, notes=None,
         legend=None, shade=None):
    """series: [{x,y,color,width,dash}]. shade: [{x0,x1,color,opacity,label}] vertical bands."""
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,Helvetica,Arial,sans-serif">']
    s.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="#ffffff" stroke="#d0d7de"/>')
    for b in (shade or []):
        x0=_sx(b['x0'],xlim); x1=_sx(b['x1'],xlim)
        s.append(f'<rect x="{x0:.1f}" y="{MT}" width="{x1-x0:.1f}" height="{PY}" fill="{b.get("color","#8c959f")}" opacity="{b.get("opacity",0.10)}"/>')
        if b.get('label'):
            s.append(f'<text x="{(x0+x1)/2:.1f}" y="{MT+PY-10}" text-anchor="middle" font-size="11" fill="{b.get("textcolor","#57606a")}">{b["label"]}</text>')
    s.append(f'<text x="{W/2}" y="27" text-anchor="middle" font-size="15" font-weight="700" fill="#1f2328">{title}</text>')
    s.append(f'<line x1="{ML}" y1="{MT}" x2="{ML}" y2="{MT+PY}" stroke="#57606a" stroke-width="1.5"/>')
    s.append(f'<line x1="{ML}" y1="{MT+PY}" x2="{ML+PX}" y2="{MT+PY}" stroke="#57606a" stroke-width="1.5"/>')
    for t in (xticks or []):
        x=_sx(t[0],xlim); s.append(f'<line x1="{x:.1f}" y1="{MT+PY}" x2="{x:.1f}" y2="{MT+PY+5}" stroke="#57606a"/>')
        s.append(f'<text x="{x:.1f}" y="{MT+PY+21}" text-anchor="middle" font-size="11.5" fill="#57606a">{t[1]}</text>')
    for t in (yticks or []):
        y=_sy(t[0],ylim); s.append(f'<line x1="{ML-5}" y1="{y:.1f}" x2="{ML}" y2="{y:.1f}" stroke="#57606a"/>')
        s.append(f'<text x="{ML-9}" y="{y+4:.1f}" text-anchor="end" font-size="11.5" fill="#57606a">{t[1]}</text>')
    for vl in (vlines or []):
        x=_sx(vl['x'],xlim)
        s.append(f'<line x1="{x:.1f}" y1="{MT}" x2="{x:.1f}" y2="{MT+PY}" stroke="{vl.get("color","#8c959f")}" stroke-width="1.2" stroke-dasharray="4 3"/>')
        if vl.get('label'): s.append(f'<text x="{x:.1f}" y="{MT-5}" text-anchor="middle" font-size="11" fill="{vl.get("color","#8c959f")}">{vl["label"]}</text>')
    for ser in series:
        pts=" ".join(f"{_sx(xx,xlim):.1f},{_sy(yy,ylim):.1f}" for xx,yy in zip(ser['x'],ser['y']))
        dash=f' stroke-dasharray="{ser["dash"]}"' if ser.get('dash') else ''
        s.append(f'<polyline points="{pts}" fill="none" stroke="{ser.get("color","#1f6feb")}" stroke-width="{ser.get("width",2.6)}"{dash}/>')
    for p in (points or []):
        s.append(f'<circle cx="{_sx(p["x"],xlim):.1f}" cy="{_sy(p["y"],ylim):.1f}" r="4.5" fill="{p.get("color","#2ea44f")}"/>')
        if p.get('label'):
            anc=p.get('anchor','start'); dx=8 if anc=='start' else -8
            s.append(f'<text x="{_sx(p["x"],xlim)+dx:.1f}" y="{_sy(p["y"],ylim)-7:.1f}" text-anchor="{anc}" font-size="11.5" font-weight="600" fill="#1f2328">{p["label"]}</text>')
    for n in (notes or []):
        s.append(f'<text x="{_sx(n["x"],xlim):.1f}" y="{_sy(n["y"],ylim):.1f}" text-anchor="{n.get("anchor","start")}" font-size="11.5" fill="{n.get("color","#57606a")}">{n["t"]}</text>')
    if legend:
        for i,(lab,col) in enumerate(legend):
            yy=MT+10+i*19
            s.append(f'<line x1="{ML+14}" y1="{yy}" x2="{ML+38}" y2="{yy}" stroke="{col}" stroke-width="3"/>')
            s.append(f'<text x="{ML+44}" y="{yy+4}" font-size="11.5" fill="#1f2328">{lab}</text>')
    s.append(f'<text x="{ML+PX/2}" y="{H-18}" text-anchor="middle" font-size="12.5" fill="#1f2328">{xlabel}</text>')
    s.append(f'<text transform="translate(20,{MT+PY/2}) rotate(-90)" text-anchor="middle" font-size="12.5" fill="#1f2328">{ylabel}</text>')
    s.append('</svg>')
    open(path,"w").write("\n".join(s))
    return path
