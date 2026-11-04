// Dynamic enclosing marks and double diacritics, Unicode 18 §3.6 P6–P8.
import outlines from './combining-outline-manifest.js';
import emoji from './emoji-manifest.js';
import { graphemes } from './unicode.js';
import { hasJoiningCharacters, hasVariationSelectors, isVariationSelector, nativeVariationFont, nativeVariationCandidates, variationFontContains } from './font-variations.js';
import { generalCategory } from './unicode-data.js';
import { lookup } from './vendor/linebreak/LineBreak.js';
import { requiresEgyptianLayout } from './egyptian-layout.js';

const shapes=new Map([[0x1abe,'parentheses'],[0x20dd,'circle'],[0x20de,'square'],[0x20df,'diamond'],[0x20e0,'circle'],[0x20e2,'screen'],[0x20e3,'keycap'],[0x20e4,'triangle']]);
for(const cp of [0x488,0x489,0xa670,0xa671,0xa672])shapes.set(cp,'numeric');
const knownEmoji=new Set(emoji.sequences);
const specialPoints=[...shapes.keys(),...Object.entries(outlines.marks).filter(([,e])=>[233,234].includes(e.ccc)).map(([cp])=>Number(cp))];
const special=new RegExp('['+specialPoints.map(cp=>'\\u{'+cp.toString(16)+'}').join('')+']','u');
const character=c=>typeof c==='string'?c:c.char;
const entry=c=>typeof c==='string'?outlines.marks[c.codePointAt(0)]:c.record;
const double=c=>[233,234].includes(entry(c)?.ccc);
const isCGJ=c=>character(c)==='\u034f';
export const hasCombiningAnnotations=text=>special.test(text)||hasVariationSelectors(text);
export const hasConnectedEgyptian=text=>requiresEgyptianLayout(text)||/[\u{13430}-\u{13455}]/u.test(text);

function canonicalMarks(chars) {
  const result=[];let pending=[];
  const flush=()=>{result.push(...pending.sort((a,b)=>(entry(a)?.ccc??0)-(entry(b)?.ccc??0)));pending=[];};
  for(const c of chars){if(!entry(c)?.ccc){flush();result.push(c);}else pending.push(c);}
  flush();return result;
}

function variationPrefix(text) {
  if(!hasVariationSelectors(text)||nativeVariationFont(text))return null;
  const chars=canonicalMarks([...text]);
  // Only the base's selector and genuine nonspacing drawings belong here.
  // CGJ is a zero-ink canonical-order boundary, retained by canonicalMarks.
  // Other contextual controls and spacing vowels need native shaping.
  if(chars.slice(1).some((c,i)=>isVariationSelector(c.codePointAt(0))?i!==0:!isCGJ(c)&&(!entry(c)?.bounds||entry(c).category==='Me'&&!shapes.has(c.codePointAt(0)))))return null;
  let best;
  for(const font of nativeVariationCandidates(text)){
    const index=chars.findIndex(c=>!isCGJ(c)&&!isVariationSelector(c.codePointAt(0))&&!variationFontContains(font.ranges,c.codePointAt(0)));
    if(index>1&&(!best||index>best.index))best={font,index};
  }
  if(!best)return null;
  const {font,index}=best,body=chars.slice(0,index).join('');
  if(nativeVariationFont(body)?.family!==font.family)return null;
  const native=outlines.variationMarks?.[font.family];
  const operations=chars.slice(index).map(c=>{
    if(isCGJ(c))return c;
    if(!variationFontContains(font.ranges,c.codePointAt(0)))return c;
    const row=native?.marks[c.codePointAt(0)],drawing=row&&outlines.variantDrawings[row.drawing];
    return drawing?.bounds?{char:c,record:{...entry(c),...drawing,source:native.source,glyph:row.glyph},nativeFamily:font.family}:null;
  });
  if(operations.some(c=>!c))return null;
  return {body,operations,variantFamily:font.family};
}

export function annotationPlan(cluster) {
  if(!hasCombiningAnnotations(cluster)||cluster.length>512||cluster.includes('\u200d'))return null;
  const chars=[...cluster],base=chars[0];
  if(hasJoiningCharacters(base)||!/^[LNPS]/.test(lookup(generalCategory,base.codePointAt(0),''))||knownEmoji.has(base)||knownEmoji.has(cluster))return null;
  const enclosures=chars.filter(c=>shapes.has(c.codePointAt(0)));
  const doubles=chars.filter(double);
  // Only nonjoining variation clusters have the native-prefix/foreign-mark
  // path below. Keep other CGJ contexts, particularly doubles, native.
  if(cluster.includes('\u034f')&&(!hasVariationSelectors(cluster)||doubles.length))return null;
  // Unicode leaves enclosure/double interaction unspecified; retain its native
  // rendering instead of inventing a nesting order.
  if(enclosures.length>16||enclosures.length&&doubles.length)return null;
  if(doubles.length) {
    const body=chars.filter(c=>!double(c)).join('');
    return {...(variationPrefix(body)??{body,operations:[]}),doubles};
  }
  const first=chars.findIndex(c=>shapes.has(c.codePointAt(0)));
  if(first<1){const partial=variationPrefix(cluster);return partial?{...partial,doubles:[]}:null;}
  const tail=chars.slice(first);
  if(tail.some(c=>!isCGJ(c)&&(!entry(c)?.bounds||entry(c).category==='Me'&&!shapes.has(c.codePointAt(0)))))return null;
  // Canonical ordering within each segment bounded by ccc=0, without relying
  // on the browser's Unicode version. Enclosing marks are such boundaries.
  const prefix=chars.slice(0,first).join(''),partial=variationPrefix(prefix);
  return {body:partial?.body??prefix,operations:[...(partial?.operations??[]),...canonicalMarks(tail)],doubles:[],...(partial?{variantFamily:partial.variantFamily}:{})};
}

export const annotationFontText=cluster=>annotationPlan(cluster)?.body??cluster;

function glyphsFor(text,m,direction) {
  if(m.runs)return m.runs.flatMap(r=>r.glyphs?r.glyphs.map(g=>({...g,x:g.x+r.offset,y:g.y+(r.baselineOffset??0)})):[{drawText:r.drawText,font:r.font,direction:r.direction,x:r.offset,y:r.baselineOffset??0,scale:1,strokeWidth:r.strokeWidth}]);
  return m.glyphs??[{drawText:text,font:m.font,direction,x:0,y:0,scale:1,strokeWidth:m.strokeWidth}];
}

function outlineGlyph(c,frame,kind='mark',size) {
  const mark=entry(c),[x0,y0,x1,y1]=mark.bounds;
  const sx=frame.width/(x1-x0),sy=frame.height/(y1-y0);
  const glyph={primitive:'outline',annotation:kind,codepoint:character(c).codePointAt(0),path:mark.path,pathOffset:[-x0,-y0],x:frame.left,y:frame.top,scale:sy,stretchX:sx/sy,frame,...(typeof c==='object'?{nativeMarkFamily:c.nativeFamily}:{})};
  if(kind==='enclosure'&&mark.ring){
    const inner=mark.ring.inner,[ix0,iy0,ix1,iy1]=inner.bounds;
    const w=frame.width-((x1-x0)-(ix1-ix0))*size,h=frame.height-((y1-y0)-(iy1-iy0))*size;
    const isx=w/(ix1-ix0),isy=h/(iy1-iy0);
    const cx=frame.width/2+((ix0+ix1)-(x0+x1))*size/2,cy=frame.height/2+((iy0+iy1)-(y0+y1))*size/2;
    glyph.contours=[{path:mark.ring.outer.path,matrix:[sx,0,0,sy,-x0*sx,-y0*sy]},
      {path:inner.path,matrix:[isx,0,0,isy,cx-(ix0+ix1)*isx/2,cy-(iy0+iy1)*isy/2]}];
    glyph.scale=glyph.stretchX=1;glyph.pathOffset=[0,0];
  }
  return glyph;
}

function include(box,left,top,right,bottom) {
  box.left=Math.min(box.left,left);box.top=Math.min(box.top,top);
  box.right=Math.max(box.right,right);box.bottom=Math.max(box.bottom,bottom);
}

function enclose(box,c,size) {
  const shape=shapes.get(c.codePointAt(0)),mark=entry(c),gap=size*.09;
  if(shape==='numeric'){encloseNumeric(box,c,size,gap);return;}
  const w=box.right-box.left+gap*2,h=box.bottom-box.top+gap*2;
  const centerX=(box.left+box.right)/2,centerY=(box.top+box.bottom)/2;
  const [x0,y0,x1,y1]=mark.ring?.inner.bounds??mark.contentBounds??mark.bounds;
  let width=w,height=h,cy=centerY;
  if(shape==='circle') {
    // Successive equal enclosures grow by padding; re-enclosing a circle's
    // bounding rectangle would otherwise cause artificial exponential growth.
    const diameter=box.outerShape==='circle'?Math.max(w,h):Math.hypot(w,h);
    width=height=diameter;
  }else if(shape==='square')width=height=Math.max(w,h);
  else if(shape==='screen'||shape==='keycap'){
    const scale=Math.max(w/(x1-x0),h/(y1-y0));
    width=(x1-x0)*scale;height=(y1-y0)*scale;
  }else if(shape==='diamond')width=height=box.outerShape==='diamond'?Math.max(w,h):w+h;
  else if(shape==='triangle') {
    const ratio=(x1-x0)/(y1-y0);
    if(box.outerShape==='triangle'){
      height=Math.max(w/ratio,h);width=height*ratio;
      cy+=(box.bottom-box.top-height)/6;
    }else{
      height=Math.max(1.5*w/ratio+.75*h,1.5*h);width=height*ratio;cy-=height/6;
    }
  }
  let cx=centerX;
  if(mark.ring){
    const [ox0,oy0,ox1,oy1]=mark.bounds,innerHeight=height;
    width+=((ox1-ox0)-(x1-x0))*size;height+=((oy1-oy0)-(y1-y0))*size;
    if(['circle','square','diamond'].includes(shape))width=height=Math.max(width,height);
    else if(['triangle','screen','keycap'].includes(shape)){
      const ratio=(ox1-ox0)/(oy1-oy0);height=Math.max(height,width/ratio);width=height*ratio;
    }
    cx-=((x0+x1)-(ox0+ox1))*size/2;cy-=((y0+y1)-(oy0+oy1))*size/2;
    if(shape==='triangle')cy-=(height-((oy1-oy0)-(y1-y0))*size-innerHeight)/6;
  }else if(mark.contentBounds){
    const [ox0,oy0,ox1,oy1]=mark.bounds;
    const scale=Math.max(width/(x1-x0),height/(y1-y0));
    cx-=((x0+x1)-(ox0+ox1))*scale/2;cy-=((y0+y1)-(oy0+oy1))*scale/2;
    width=(ox1-ox0)*scale;height=(oy1-oy0)*scale;
  }
  const frame={left:cx-width/2,top:cy-height/2,width,height};
  box.glyphs.push(outlineGlyph(c,frame,'enclosure',size));
  include(box,frame.left,frame.top,frame.left+width,frame.top+height);
  box.outerShape=shape;
}

function encloseNumeric(box,c,size,gap) {
  const mark=entry(c),data=mark.numericEnclosure;
  const cx=(box.left+box.right)/2,cy=(box.top+box.bottom)/2;
  const [x0,y0,x1,y1]=mark.bounds,ox=(x0+x1)/2,oy=(y0+y1)/2;
  const parts=data.parts;
  const radius=Math.max(...parts.map(p=>Math.hypot(p.bounds[2]-p.bounds[0],p.bounds[3]-p.bounds[1])*size/2));
  const halfW=(box.right-box.left)/2,halfH=(box.bottom-box.top)/2;
  const orbit=(box.outerShape==='circle'?Math.max(halfW,halfH)+gap:Math.hypot(halfW+gap,halfH+gap))+radius;
  for(const part of parts){
    let path=part.path,[a,b,d,e]=part.bounds,dx=0,dy=0;
    if(data.kind==='radial'){
      const x=(a+d)/2-ox,y=(b+e)/2-oy,length=Math.hypot(x,y);
      dx=cx+x/length*orbit-(a+d)*size/2;
      dy=cy+y/length*orbit-(b+e)*size/2;
    }else if(data.kind==='sides'){
      if(part.side==='left'||part.side==='right'){
        dx=part.side==='left'?box.left-gap-d*size:box.right+gap-a*size;
        dy=cy-oy*size;
      }else{
        dx=cx-ox*size;
        dy=part.side==='top'?box.top-gap-e*size:box.bottom+gap-b*size;
      }
    }else{
      const widening=Math.max(0,(halfW+gap)/size-(x1-x0)/2);
      const vertices=part.vertices.map(([x,y])=>[x+Math.sign(x-ox)*widening,y]);
      path=vertices.map(([x,y],i)=>(i?'L':'M')+x+' '+y).join('')+'Z';
      a-=widening;d+=widening;dx=cx-ox*size;
      dy=(b+e)/2<oy?box.top-gap-e*size:box.bottom+gap-b*size;
    }
    const frame={left:a*size+dx,top:b*size+dy,width:(d-a)*size,height:(e-b)*size};
    box.glyphs.push({primitive:'outline',annotation:'enclosure',numericEnclosure:data.kind,codepoint:c.codePointAt(0),path,pathOffset:[-a,-b],x:frame.left,y:frame.top,scale:size,stretchX:1,frame});
  }
  // Every part was placed against the same original frame. Only now enlarge
  // the measured envelope; later marks must surround the complete result.
  for(const g of box.glyphs.slice(-parts.length))include(box,g.frame.left,g.frame.top,g.frame.left+g.frame.width,g.frame.top+g.frame.height);
  box.outerShape=data.kind==='radial'?'circle':null;
}

function appendMark(box,c,size) {
  const mark=entry(c),[x0,y0,x1,y1]=mark.bounds;
  const w=(x1-x0)*size,h=(y1-y0)*size,ccc=mark.ccc;
  const gap=[200,202,214,216].includes(ccc)?0:size*.035;
  // Explicit positional classes take precedence over the source glyph's
  // baseline-relative coordinates (a horn can be drawn below its own origin).
  const side=ccc===1||mark.category==='Me'?'overlay':ccc===224?'left':ccc===226?'right':[200,202,204,218,220,222,233,240].includes(ccc)?'below':[8,214,216,228,230,232,234].includes(ccc)?'above':y0>=0?'below':'above';
  const anchor=box.anchorFrame??box;
  let x=(anchor.left+anchor.right-w)/2,y=(anchor.top+anchor.bottom-h)/2;
  if(side==='above')y=box.top-gap-h;
  if(side==='below')y=box.bottom+gap;
  if(side==='left')x=box.left-gap-w;
  if(side==='right')x=box.right+gap;
  if([200,218,228].includes(ccc))x=anchor.left-w/2;
  if([8,216,222,232].includes(ccc))x=anchor.right-w/2;
  box.glyphs.push(outlineGlyph(c,{left:x,top:y,width:w,height:h}));
  const previous=[box.left,box.top,box.right,box.bottom];
  include(box,x,y,x+w,y+h);
  if(previous.some((value,i)=>value!==[box.left,box.top,box.right,box.bottom][i]))box.outerShape=null;
}

export function combiningInk(text,size,measure,direction='ltr') {
  if(!hasCombiningAnnotations(text)||hasConnectedEgyptian(text))return null;
  const logical=text.replace(/^[\u202a-\u202e]/u,'').replace(/\u202c$/u,'');
  const clusters=graphemes(logical),plans=clusters.map(annotationPlan);
  if(!plans.some(Boolean))return null;
  const boxes=[];
  for(let i=0;i<clusters.length;){
    let source=clusters[i],plan=plans[i],count=1;
    if(!plan&&!plans[i-1]?.doubles.length){while(i+count<clusters.length&&!plans[i+count]){source+=clusters[i+count];count++;}}
    const body=plan?.body??source,m=measure(body,size,direction);
    const box={source,body,plan,advance:m.advance,left:-m.drawOffset,right:m.width-m.drawOffset,top:-m.ascent,bottom:m.descent,glyphs:glyphsFor(body,m,direction)};
    for(const c of plan?.operations??[])if(isCGJ(c))continue;else if(shapes.has(character(c).codePointAt(0))){
      enclose(box,c,size);box.anchorFrame={left:box.left,right:box.right,top:box.top,bottom:box.bottom};
    }else appendMark(box,c,size);
    if(plan?.operations.length){
      const pad=Math.max(0,-box.left);
      box.glyphs=box.glyphs.map(g=>({...g,x:g.x+pad}));
      box.right+=pad;box.left+=pad;box.advance=Math.max(box.advance+pad,box.right);
    }
    boxes.push(box);i+=count;
  }
  // Draw doubles after both bases' normal accents, at the outermost layer.
  // Do not merge the logical graphemes: editing, sharing and UAX29 stay intact.
  const visual=direction==='rtl'?[...boxes].reverse():boxes;
  let advance=0;
  for(const box of visual){box.offset=advance;advance+=box.advance;}
  for(let i=0;i<boxes.length;i++)for(const c of boxes[i].plan?.doubles??[]){
    const a=boxes[i],b=boxes[i+1]??a,mark=entry(c);
    const ax=a.offset+(a.left+a.right)/2,bx=b===a?ax+Math.max(size*.5,a.advance):b.offset+(b.left+b.right)/2;
    const left=Math.min(ax,bx)-size*.12,width=Math.abs(ax-bx)+size*.24;
    const height=(mark.bounds[3]-mark.bounds[1])*size;
    const top=mark.ccc===233?Math.max(a.bottom,b.bottom)+size*.035:Math.min(a.top,b.top)-height-size*.035;
    const frame={left:left-a.offset,top,width,height};
    a.glyphs.push(outlineGlyph(c,frame,'double'));
    include(a,frame.left,top,frame.left+width,top+height);
  }
  const glyphs=visual.flatMap(b=>b.glyphs.map(g=>({...g,x:g.x+b.offset})));
  const left=Math.min(0,...boxes.map(b=>b.offset+b.left)),right=Math.max(advance,...boxes.map(b=>b.offset+b.right));
  return {fontSize:size,width:right-left,advance,drawOffset:-left,ascent:Math.max(0,...boxes.map(b=>-b.top)),descent:Math.max(0,...boxes.map(b=>b.bottom)),glyphs,annotationLayout:true};
}
