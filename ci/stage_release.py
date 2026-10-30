#!/usr/bin/env python3
"""Select package-only roothide metadata; never change runtime or execute hooks.
Pinned Theos wraps the install prefix after before-package, so staging paths
are unprefixed here. DEBIAN/control is already generated.
"""
from pathlib import Path
import argparse
ROOT=Path(__file__).resolve().parents[1]
ARCH={'roothide':'iphoneos-arm64e'}

def stage_release(stage,scheme):
    if scheme not in ARCH: raise ValueError('unsupported package scheme')
    stage=Path(stage).resolve()
    if stage==Path('/') or not (stage/'usr/libexec/vedette-nicectl').is_file():
        raise ValueError('unexpected staging directory or missing control tool')
    control=stage/'DEBIAN/control'
    if not control.is_file() or control.is_symlink(): raise ValueError('missing/unsafe staged control')
    text=control.read_text();fields=dict(line.split(':',1) for line in text.splitlines() if ':' in line)
    if fields.get('Package','').strip()!='com.doimty.vedette' or fields.get('Version','').strip()!='1.1.14-5':
        raise ValueError('wrong staged package/version')
    if fields.get('Architecture','').strip()!=ARCH[scheme]: raise ValueError('staged scheme/architecture mismatch')
    old='Depends: firmware (>= 15.0), roothide, preferenceloader, mobilesubstrate (>= 0.9.5000), com.opa334.altlist'
    if text.count(old)!=1: raise ValueError('unexpected dependency declaration')
    print('Staged '+scheme+' metadata; original recovery gates remain required.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--scheme',choices=ARCH,required=True);p.add_argument('--stage',type=Path,required=True)
    a=p.parse_args();stage_release(a.stage,a.scheme)
