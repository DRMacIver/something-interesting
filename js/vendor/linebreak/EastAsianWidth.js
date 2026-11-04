import { eastAsianWidth } from '../../unicode-data.js';
import { lookup } from './LineBreak.js';
export const EastAsianWidth = { get: cp => lookup(eastAsianWidth, cp, false) };
