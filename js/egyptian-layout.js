import enclosureManifest from './egyptian-enclosure-manifest.js';
import insertionManifest from './egyptian-insertion-manifest.js';
// Unicode 18 section 11.4: HJ binds more tightly than VJ; explicit segments
// override precedence. This path adds extended signs to basic quadrat layout.
// Unsupported controls and malformed groups stay on the native-font path.
const INSERTIONS=['\u{13432}','\u{13433}','\u{13434}','\u{13435}','\u{13439}','\u{1343a}','\u{1343b}'];
const enclosureStarts=new Set(enclosureManifest.starts.map(c=>String.fromCodePoint(c)));
const enclosureEnds=new Set(enclosureManifest.ends.map(c=>String.fromCodePoint(c)));
const enclosureOpen=c=>c==='\u{1343c}'||c==='\u{1343e}';
const MIRROR='\u{13440}';
const V='\u{13430}',H='\u{13431}',O='\u{13436}',OPEN='\u{13437}',CLOSE='\u{13438}';
const signs=/^[\u{13000}-\u{1342f}\u{13460}-\u{143ff}]$/u;
export const requiresEgyptianLayout=text => /[\u{13432}-\u{13435}\u{13439}-\u{1343f}]/u.test(text) || /\u202e[\s\S]*[\u{13000}-\u{143ff}]/u.test(text) || /[\u{13440}-\u{13455}]/u.test(text) || /[\u{13430}\u{13431}\u{13436}]/u.test(text)
  && /[\u{13460}-\u{143ff}\ufe00-\ufe06]/u.test(text);

export function parseEgyptian(text) {
  const chars=[...text];let i=0,depth=0;
  const precedence=new Map([[V,1],[H,2],[O,3],...INSERTIONS.map(c=>[c,4])]);
  function atom() {
    if (++depth>32) throw Error('depth');
    let node;
    if (enclosureOpen(chars[i]) || enclosureStarts.has(chars[i]) && enclosureOpen(chars[i+1])) {
      const start=enclosureStarts.has(chars[i])?chars[i++]:null;
      const control=chars[i++],endControl=String.fromCodePoint(control.codePointAt(0)+1);
      const content=sequence(endControl);
      if(chars[i++]!==endControl)throw Error('enclosure');
      const end=enclosureEnds.has(chars[i])?chars[i++]:null;
      node={kind:'enclosure',start,end,control,children:[content]};
    } else if (chars[i]===OPEN) {
      i++;node=sequence(CLOSE);
      if (chars[i++]!==CLOSE) throw Error('segment');
      node={...node,grouped:true};
    } else if (/^[\u{13441}-\u{13446}]$/u.test(chars[i]??'')) {
      const text=chars[i++],cp=text.codePointAt(0),lost=cp>=0x13443;
      const expanded=lost && chars[i]==='\ufe00';
      if (expanded)i++;
      node={kind:lost?'lost':'blank',text:text+(expanded?'\ufe00':''),expanded,
        width:cp===0x13442||cp===0x13444||cp===0x13445?.5:1,
        height:cp===0x13442||cp===0x13444||cp===0x13446?.5:1};
    } else {
      if (!signs.test(chars[i]??'')) throw Error('sign');
      let text=chars[i++];
      if (/^[\ufe00-\ufe06]$/u.test(chars[i]??'')) text+=chars[i++];
      const mirror=chars[i]===MIRROR;
      if (mirror)i++;
      const damage=/^[\u{13447}-\u{13455}]$/u.test(chars[i]??'')?chars[i++]:null;
      node={kind:'sign',text,mirror,damage};
    }
    depth--;return node;
  }
  function expression(minimum) {
    let left=atom();
    while ((precedence.get(chars[i])??0)>=minimum) {
      const op=chars[i++],right=expression(precedence.get(op)+1);
      if (INSERTIONS.includes(op)) {left={kind:'insertion',control:op,children:[left,right]};continue;}
      const kind=op===V?'vertical':op===H?'horizontal':'overlay';
      left=left.kind===kind?{kind,children:[...left.children,right]}:{kind,children:[left,right]};
    }
    return left;
  }
  function sequence(end=null) {
    const children=[];
    while (i<chars.length && chars[i]!==end) children.push(expression(1));
    if (!children.length) throw Error('empty segment');
    return children.length===1?children[0]:{kind:'sequence',children};
  }
  try {const tree=sequence();return i===chars.length?tree:null;} catch {return null;}
}

function move(box,x,y,scale=1) {
  return box.glyphs.map(g=>({...g,x:x+g.x*scale,y:y+g.y*scale,scale:g.scale*scale}));
}

function damageGlyphs(control,width,height,size) {
  if(!control)return [];
  const mask=control.codePointAt(0)-0x13446,glyphs=[];
  for(let quarter=0;quarter<4;quarter++)if(mask & (1<<quarter)){
    const x=quarter>=2?width/2:0,y=quarter%2?height/2:0;
    glyphs.push({primitive:'damage',sourceText:control,quarter,x,y,width:width/2,height:height/2,
      step:size*.1,stroke:size*.012,phase:(x+y)%(size*.1),scale:1});
  }
  return glyphs;
}

export function layoutEgyptian(tree,size,measure) {
  const gap=size*.06;
  function visit(node) {
    if (node.kind==='enclosure') {
      const entry=c=>enclosureManifest.entries[c.codePointAt(0).toString(16).toUpperCase()];
      const band=entry(node.control),start=node.start?entry(node.start):null,end=node.end?entry(node.end):null;
      const child=visit(node.children[0]);
      const parts=[band,...[start,end].filter(Boolean)];
      const minY=Math.min(...parts.map(p=>p.bounds[1])),maxY=Math.max(...parts.map(p=>p.bounds[3]));
      const unit=size/(maxY-minY),innerHeight=enclosureManifest.contentHeight*unit;
      const contentScale=Math.min(1,innerHeight/Math.max(child.height,1));
      const bandWidth=Math.max(band.advance,child.width*contentScale/unit+210);
      const count=Math.ceil(bandWidth/band.advance),stretch=bandWidth/(count*band.advance);
      const begin=start?.advance??0;
      const pieces=[...(start?[{part:start,x:0,stretch:1}]:[]),
        ...Array.from({length:count},(_,i)=>({part:band,x:begin+i*band.advance*stretch,stretch})),
        ...(end?[{part:end,x:begin+bandWidth,stretch:1}]:[])];
      const minX=Math.min(0,...pieces.map(p=>p.x+p.part.bounds[0]*p.stretch));
      const maxX=Math.max(begin+bandWidth+(end?.advance??0),...pieces.map(p=>p.x+p.part.bounds[2]*p.stretch));
      const glyphs=pieces.map(({part,x,stretch})=>{
        const [x0,y0,x1,y1]=part.bounds;
        return {primitive:'outline',sourceText:node.control,path:part.path,pathOffset:[-x0,-y0],
          x:(x+x0*stretch-minX)*unit,y:(y0-minY)*unit,width:(x1-x0)*stretch,height:y1-y0,stretchX:stretch,scale:unit};
      });
      glyphs.push(...move(child,(begin-minX)*unit+(bandWidth*unit-child.width*contentScale)/2,
        -minY*unit+(innerHeight-child.height*contentScale)/2,contentScale));
      return {width:(maxX-minX)*unit,height:size,glyphs};
    }
    if (node.kind==='insertion') {
      const insertions=[];let container=node;
      do {
        insertions.unshift({control:container.control,content:container.children[1]});
        container=container.children[0];
      } while(container.kind==='insertion' && !container.grouped);
      if(container.kind!=='sign') throw Error('unsupported insertion container');
      const key=[...container.text,...(container.mirror?[MIRROR]:[]),...insertions.map(i=>i.control)].map(c=>c.codePointAt(0).toString(16).toUpperCase()).join('-');
      const entry=insertionManifest.entries[key];
      if(!entry)throw Error('unreviewed insertion container');
      const factor=size/Math.max(entry.width,entry.height),regions=entry.regions??[entry.region];
      const glyphs=[{primitive:'outline',sourceText:container.text,path:entry.path,pathOffset:entry.pathOffset,
        x:0,y:0,width:entry.width,height:entry.height,scale:factor}];
      // Damage belongs to the preceding container, before inserted children.
      // Retain its native insertion drawing/coordinates and shade that surface.
      glyphs.push(...damageGlyphs(container.damage,entry.width*factor,entry.height*factor,size));
      for(const [index,{content}] of insertions.entries()) {
        const child=visit(content),[rx,ry,rw,rh]=regions[index].map(n=>n*factor);
        const scale=Math.min(1,rw/Math.max(child.width,1),rh/Math.max(child.height,1));
        glyphs.push(...move(child,rx+(rw-child.width*scale)/2,ry+(rh-child.height*scale)/2,scale));
      }
      return {width:entry.width*factor,height:entry.height*factor,glyphs};
    }
    if (node.kind==='blank'||node.kind==='lost') {
      const width=node.width*size,height=node.height*size,inset=node.expanded?0:size*.03;
      return {width,height,expanded:node.expanded,glyphs:node.kind==='blank'?[]:[{
        primitive:'lost',sourceText:node.text,x:inset,y:inset,width:width-2*inset,
        height:height-2*inset,step:size*.1,stroke:size*.012,scale:1}]};
    }
    if (node.kind==='sign') {
      const policy=/[\ufe00-\ufe06]/u.test(node.text)?'egyptian-variant':'egyptian-sign';
      const m=measure(node.text,size,policy);
      const width=m.width,height=m.ascent+m.descent;
      const glyphs=[{drawText:node.text,font:m.font,direction:'ltr',
        x:node.mirror?width-m.drawOffset:m.drawOffset,y:m.ascent,scale:1,flipX:node.mirror,strokeWidth:m.strokeWidth}];
      // Encoded order: TS=1, BS=2, TE=4, BE=8; independent of sign mirroring.
      glyphs.push(...damageGlyphs(node.damage,width,height,size));
      return {width,height,glyphs};
    }
    const children=node.kind==='sequence'?node.children.map(n=>layoutEgyptian(n,size,measure)):node.children.map(visit);
    const horizontal=['horizontal','sequence'].includes(node.kind),vertical=node.kind==='vertical';
    const gaps=children.slice(1).map((c,i)=>c.expanded && children[i].expanded?0:gap);
    const spacing=gaps.reduce((a,b)=>a+b,0);
    const width=horizontal?children.reduce((a,b)=>a+b.width,0)+spacing:Math.max(...children.map(c=>c.width));
    const height=vertical?children.reduce((a,b)=>a+b.height,0)+spacing:Math.max(...children.map(c=>c.height));
    let offset=0;const glyphs=[];
    for (const [index,child] of children.entries()) {
      glyphs.push(...move(child,horizontal?offset:(width-child.width)/2,vertical?offset:(height-child.height)/2));
      offset+=(horizontal?child.width:child.height)+(gaps[index]??0);
    }
    return {width,height,glyphs};
  }
  const natural=visit(tree);
  if (tree.kind==='sequence'||tree.kind==='enclosure') return natural;
  const scale=Math.min(1,size/Math.max(natural.width,1),size/Math.max(natural.height,1));
  return {width:natural.width*scale,height:natural.height*scale,expanded:natural.expanded,glyphs:move(natural,0,0,scale)};
}

export function egyptianInk(text,size,measure,direction='ltr') {
  const rtl=direction==='rtl';
  if (!requiresEgyptianLayout(text) && !(rtl && /[\u{13000}-\u{143ff}]/u.test(text))) return null;
  // Bidi overrides are added by the renderer, outside the logical signs.
  const logical=text.replace(/^[\u202a-\u202e]/u,'').replace(/\u202c$/u,'');
  const chunks=logical.split(/([\u{13000}-\u{143ff}\ufe00-\ufe06]+)/u).filter(Boolean);
  let handled=false,advance=0,ascent=0,descent=0;const parts=[];
  for (const chunk of chunks) {
    let box=null;
    const tree=parseEgyptian(chunk);
    if(tree) {try {box=layoutEgyptian(tree,size,measure);} catch { /* Preserve unsupported native shaping. */ }}
    if (box) {
      handled=true;
      // Place each quadrat on the baseline; preserve normal text descent.
      parts.push({x:advance,box,egyptian:true});advance+=box.width;ascent=Math.max(ascent,box.height);
    } else {
      const m=measure(chunk,size,'text',direction);
      parts.push({x:advance,box:{width:m.width,height:m.ascent+m.descent,glyphs:[{drawText:rtl?'\u202e'+chunk+'\u202c':chunk,font:m.font,direction,x:m.drawOffset,y:m.ascent,scale:1}]},baseline:m.ascent});
      advance+=m.width;ascent=Math.max(ascent,m.ascent);descent=Math.max(descent,m.descent);
    }
  }
  if (!handled)return null;
  const glyphs=parts.flatMap(({x,box,egyptian,baseline=box.height})=>{
    if (!rtl)return move(box,x,-baseline);
    const reflected=egyptian?{...box,glyphs:box.glyphs.map(g=>g.primitive && g.primitive!=='outline'
      ? {...g,x:box.width-g.x-g.width*g.scale}
      : {...g,x:box.width-g.x,flipX:!g.flipX})}:box;
    return move(reflected,advance-x-box.width,-baseline);
  });
  return {fontSize:size,width:advance,advance,drawOffset:0,ascent,descent,glyphs};
}

// Line-breaking must not tear an explicit segment apart, even where its
// adjacent signs or spaces otherwise allow an emergency/default break.
export function egyptianSegmentInteriors(text) {
  const positions=new Set();let depth=0,offset=0;
  const chars=[...text];
  for (const [i,char] of chars.entries()) {
    if (char===OPEN || enclosureOpen(char))depth++;
    if (char===CLOSE || char==='\u{1343d}' || char==='\u{1343f}')depth=Math.max(0,depth-1);
    offset+=char.length;
    if (depth || enclosureStarts.has(char) && enclosureOpen(chars[i+1]) ||
        (char==='\u{1343d}'||char==='\u{1343f}') && enclosureEnds.has(chars[i+1]))positions.add(offset);
  }
  return positions;
}
