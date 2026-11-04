"""Reviewed activity SVG geometry and exposed-skin regions."""
import hashlib,json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage
import pymupdf
import copy
from functools import lru_cache
from skimage.measure import find_contours,approximate_polygon
from pen_translate import Settings,translate,same_features
ROOT=Path(__file__).resolve().parents[2]
# expected shape count, retained paint, solid ink, exposed skin
RECIPES={
 '1f483':(43,{0}|set(range(2,8))|{9,10}|set(range(12,17))|set(range(18,34))|{37,39,40,41,42},{6,7,15,28,29,30,31,32,33,37,40,41,42},{0,9,10,13,16,26,27,39}),
 '1f57a':(31,set(range(8))|set(range(9,31)),{0,1,17}|set(range(19,25))|set(range(26,31)),{6,7,9,12,15,16,18}),
 '1f9ce':(16,set(range(12)),{0,2,5,6,7,11},{4,9}),
 '1f9ce_200d_2642':(13,set(range(12)),{0,2,5,6,7,11},{4,9}),
 '1f9ce_200d_2640':(17,set(range(12))|{15},{0,2,5,6,7,11,15},{4,9}),
 '1f3c3':(26,set(range(11))|{12,13,14,15,16,17,18,20,21},{1,2,3,5,7,20,21},{0,8,12,13,15,16,17,18}),
 '1f3c3_200d_2642':(23,set(range(11))|{12,13,14,15,16,17,18,20,21},{1,2,3,5,7,20,21},{0,8,12,13,15,16,17,18}),
 '1f3c3_200d_2640':(27,{0}|set(range(4,14))|{15,16,18,19,20,21,22,23,24,26},{0,5,7,9,10,12,13,26},{8,11,18,19,21,22,23,24}),
 '1f6b6':(21,set(range(17)),{1,2,3,9,10,11,12,13,14,16},{0,7,8}),
 '1f6b6_200d_2642':(18,set(range(17)),{1,2,3,9,10,11,12,13,14,16},{0,7,8}),
 '1f6b6_200d_2640':(22,{0}|set(range(4,21)),{0,5,6,7,13,14,15,16,17,18,20},{4,11,12}),
 '1f9cd':(28,{0,1,2}|set(range(5,14))|{15,16}|set(range(19,28)),{0}|set(range(5,13))|set(range(22,28)),{1,2,15,19,20,21}),
 '1f9cd_200d_2642':(28,{0,1}|set(range(4,13))|{14,15}|set(range(18,28)),set(range(4,12))|{20}|set(range(22,28)),{0,1,14,18,19,21}),
 '1f9cd_200d_2640':(26,{0,1,2,3}|set(range(6,13))|{14,15,16,17}|set(range(20,26)),{0,1}|set(range(6,12))|{14}|set(range(20,26)),{2,3,15,16}),
}

EXTRA_ACTIVITY_KEYS={'1f487_200d_2642', '1f486_200d_2642', '1f9d1_200d_1fa70', '1f486', '1f487_200d_2640', '1f574', '1f487', '1f486_200d_2640'}
RECIPES.update({'1f486': (14, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}, {0, 6, 7, 8, 9, 10, 11}, {1, 2, 3, 4, 12, 13}), '1f486_200d_2642': (14, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13}, {4, 6, 7, 8, 9, 10, 11}, {0, 2, 3, 5, 12, 13}), '1f486_200d_2640': (12, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11}, {0, 6, 7, 8, 9, 10, 11}, {1, 3, 4, 5}), '1f487': (20, {0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19}, {0, 3, 9, 10, 11, 12, 13, 14, 15, 18, 19}, {8, 4, 5, 7}), '1f487_200d_2642': (20, {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18, 19}, {2, 3, 9, 10, 11, 12, 13, 14, 15, 18, 19}, {8, 4, 5, 7}), '1f487_200d_2640': (17, {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15, 16}, {2, 3, 7, 8, 9, 10, 11, 12, 15, 16}, {5, 6}), '1f574': (40, {0, 1, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39}, {0, 1, 34, 35, 33, 36, 37, 38, 39, 11, 13, 15, 19, 21, 22}, {32, 8, 9, 10, 31}), '1f9d1_200d_1fa70': (22, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 20, 21}, {1, 6, 7, 8, 9, 10, 11, 12, 17, 20, 21}, {0, 2, 3, 4, 5, 13, 15})})

MOBILITY_KEYS={'1f9d1_200d_1f9bc', '1f468_200d_1f9af', '1f468_200d_1f9af_200d_27a1', '1f469_200d_1f9bc', '1f469_200d_1f9bd_200d_27a1', '1f469_200d_1f9bd', '1f468_200d_1f9bd_200d_27a1', '1f9d1_200d_1f9bd', '1f468_200d_1f9bd', '1f469_200d_1f9af_200d_27a1', '1f469_200d_1f9bc_200d_27a1', '1f9d1_200d_1f9af', '1f468_200d_1f9bc', '1f9d1_200d_1f9bc_200d_27a1', '1f9d1_200d_1f9bd_200d_27a1', '1f468_200d_1f9bc_200d_27a1', '1f469_200d_1f9af', '1f9d1_200d_1f9af_200d_27a1'}
RECIPES.update({'1f9d1_200d_1f9af': (25, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17}, {1, 2, 3, 5, 7, 8, 9, 10, 11, 16, 17}, {0, 13, 14}), '1f468_200d_1f9af': (19, {0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18}, {1, 2, 3, 4, 7, 9, 10, 11, 12, 13, 18}, {0, 16, 15}), '1f469_200d_1f9af': (23, {0, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22}, {0, 5, 6, 7, 8, 11, 13, 14, 15, 16, 17, 22}, {19, 4, 20}), '1f9d1_200d_1f9af_200d_27a1': (25, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17}, {1, 2, 3, 5, 7, 8, 9, 10, 11, 16, 17}, {0, 13, 14}), '1f468_200d_1f9af_200d_27a1': (19, {0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18}, {1, 2, 3, 4, 7, 9, 10, 11, 12, 13, 18}, {0, 16, 15}), '1f469_200d_1f9af_200d_27a1': (23, {0, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22}, {0, 5, 6, 7, 8, 11, 13, 14, 15, 16, 17, 22}, {19, 4, 20}), '1f9d1_200d_1f9bd': (40, {0, 1, 2, 3, 4, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39}, {1, 2, 3, 4, 12, 15, 16, 17, 19, 20, 21, 23, 24, 29, 30, 32, 33, 34}, {0, 36, 37, 38}), '1f468_200d_1f9bd': (34, {0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33}, {1, 2, 4, 5, 6, 9, 10, 11, 13, 14, 15, 17, 18, 23, 24, 27, 28, 29}, {0, 32, 30, 31}), '1f469_200d_1f9bd': (37, {0, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36}, {0, 4, 5, 7, 8, 9, 12, 13, 14, 16, 17, 18, 20, 21, 26, 27, 29, 30, 31}, {33, 34, 3, 35}), '1f9d1_200d_1f9bd_200d_27a1': (40, {0, 1, 2, 3, 4, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39}, {1, 2, 3, 4, 12, 15, 16, 17, 19, 20, 21, 23, 24, 29, 30, 32, 33, 34}, {0, 36, 37, 38}), '1f468_200d_1f9bd_200d_27a1': (34, {0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33}, {1, 2, 4, 5, 6, 9, 10, 11, 13, 14, 15, 17, 18, 23, 24, 27, 28, 29}, {0, 32, 30, 31}), '1f469_200d_1f9bd_200d_27a1': (37, {0, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36}, {0, 4, 5, 7, 8, 9, 12, 13, 14, 16, 17, 18, 20, 21, 26, 27, 29, 30, 31}, {33, 34, 3, 35}), '1f9d1_200d_1f9bc': (46, {0, 1, 2, 3, 4, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45}, {1, 2, 3, 4, 12, 15, 17, 18, 19, 21, 22, 23, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42}, {0, 44}), '1f468_200d_1f9bc': (40, {0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 38, 39}, {1, 2, 3, 4, 6, 9, 11, 12, 13, 15, 16, 17, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36}, {0, 38}), '1f469_200d_1f9bc': (42, {0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40}, {1, 2, 4, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 38, 39, 40}, {0, 36}), '1f9d1_200d_1f9bc_200d_27a1': (46, {0, 1, 2, 3, 4, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45}, {1, 2, 3, 4, 12, 15, 17, 18, 19, 21, 22, 23, 25, 26, 27, 29, 30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 42}, {0, 44}), '1f468_200d_1f9bc_200d_27a1': (40, {0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 38, 39}, {1, 2, 3, 4, 6, 9, 11, 12, 13, 15, 16, 17, 19, 20, 21, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 34, 35, 36}, {0, 38}), '1f469_200d_1f9bc_200d_27a1': (42, {0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40}, {1, 2, 4, 7, 9, 10, 11, 13, 14, 15, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 31, 32, 33, 34, 38, 39, 40}, {0, 36})})

RECIPES.update({'1f46f': (78, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 47, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 71, 72, 73, 74, 75, 76, 77}, {64, 1, 6, 7, 71, 10, 74, 12, 75, 14, 76, 77, 19, 20, 21, 30, 32, 36, 37, 38, 39, 40, 47, 54, 60, 61, 62, 63}, {0, 2, 3, 4, 5, 8, 9, 11, 13, 15, 16, 17, 18, 28, 29, 31, 33, 34, 35, 57, 58, 59}), '1f46f_200d_2642': (54, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 52, 53}, {1, 6, 7, 10, 12, 14, 19, 20, 23, 25, 29, 30, 31, 32, 33, 34, 35, 37, 43, 44, 45, 46, 47, 48, 49, 51}, {0, 2, 3, 4, 5, 8, 9, 11, 13, 15, 16, 17, 18, 21, 22, 24, 26, 27, 28, 40, 41, 42}), '1f46f_200d_2640': (56, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 23, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 51, 53, 54, 55}, {1, 2, 7, 8, 11, 15, 16, 17, 18, 19, 20, 21, 23, 25, 29, 30, 35, 36, 39, 43, 44, 45, 46, 47, 48, 49, 51, 53}, {0, 3, 4, 5, 6, 9, 10, 12, 13, 14, 28, 31, 32, 33, 34, 37, 38, 40, 41, 42})})

RECIPES.update({'1f9d6': (34, {32, 33, 2, 9, 10, 11, 14, 17, 18, 19, 20, 21, 22, 23, 24, 25}, {2, 19, 20, 21, 22, 23, 24, 25}, {17, 10, 18, 14}), '1f9d6_200d_2642': (22, {2, 3, 4, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21}, {12, 13, 14, 15, 16, 17, 18}, {11, 10, 3, 7}), '1f9d6_200d_2640': (23, {2, 4, 5, 6, 9, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22}, {2, 13, 15, 16, 17, 18, 19, 20}, {9, 12, 5}), '1f9d7': (35, {0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34}, {0, 32, 33, 34, 4, 5, 6, 7, 9, 14, 18, 20, 27, 28, 29, 30, 31}, {1, 3, 11, 15, 21, 22, 24, 25}), '1f9d7_200d_2642': (35, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34}, {0, 32, 33, 34, 6, 11, 12, 13, 14, 16, 18, 20, 27, 28, 29, 30, 31}, {1, 3, 7, 10, 21, 22, 24, 25}), '1f9d7_200d_2640': (39, {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 37, 38}, {0, 6, 10, 12, 13, 14, 15, 18, 25, 26, 27, 28, 29, 30, 31, 32, 33, 37}, {1, 3, 7, 11, 19, 20, 22, 23})})

RECIPES.update({key+'_200d_27a1':value for key,value in list(RECIPES.items()) if key.split('_')[0] in {'1f3c3','1f6b6','1f9ce'}})

EXPECTED_REGIONS={'1f3c3': [15, [1, 3, 5, 6, 7, 9, 10, 11, 13]], '1f3c3_200d_2642': [16, [1, 3, 5, 6, 7, 9, 10, 11, 12, 14]], '1f3c3_200d_2640': [16, [1, 4, 5, 6, 7, 9, 10, 11, 12, 14]], '1f3c3_200d_27a1': [16, [1, 3, 4, 6, 7, 8, 10, 11, 12, 13, 14]], '1f3c3_200d_2642_200d_27a1': [16, [1, 4, 5, 6, 7, 9, 10, 11, 12, 14]], '1f3c3_200d_2640_200d_27a1': [16, [1, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14]], '1f6b6': [9, [1, 6, 9]], '1f6b6_200d_2642': [9, [1, 5, 8]], '1f6b6_200d_2640': [9, [1, 5, 8]], '1f6b6_200d_27a1': [9, [1, 4, 5, 9]], '1f6b6_200d_2642_200d_27a1': [9, [1, 5, 8]], '1f6b6_200d_2640_200d_27a1': [9, [1, 5, 7, 9]], '1f9cd': [9, [1, 2, 3, 4, 6, 7]], '1f9cd_200d_2642': [9, [1, 2, 3, 4, 6, 7]], '1f9cd_200d_2640': [7, [1, 2, 4, 5]], '1f9ce': [6, [1, 4]], '1f9ce_200d_2642': [6, [1, 4]], '1f9ce_200d_2640': [6, [1, 4]], '1f9ce_200d_27a1': [6, [1, 4]], '1f9ce_200d_2642_200d_27a1': [6, [1, 4]], '1f9ce_200d_2640_200d_27a1': [6, [1, 4]]}

EXPECTED_REGIONS.update({'1f483': [27, [1, 2, 6, 9, 11, 22, 26]], '1f57a': [16, [1, 2, 3, 5, 6, 9, 11, 16]]})

EXPECTED_REGIONS.update({'1f9d6': [9, [1, 3, 6, 8]], '1f9d6_200d_2642': [9, [1, 2, 3, 6, 8]], '1f9d6_200d_2640': [7, [1, 4, 6]], '1f9d7': [26, [3, 5, 8, 9, 11, 14, 16, 18, 21, 24]], '1f9d7_200d_2642': [26, [3, 6, 8, 9, 10, 13, 16, 18, 21, 24]], '1f9d7_200d_2640': [26, [3, 6, 8, 9, 10, 13, 16, 18, 21, 24]]})

EXPECTED_REGIONS.update({'1f46f': [28, [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 25, 26, 27, 28]], '1f46f_200d_2642': [28, [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 25, 26, 27, 28]], '1f46f_200d_2640': [24, [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 21, 22, 23, 24]]})

@lru_cache(maxsize=6)
def leg_union(raw,indices):
 # Join the source's overlapping thigh/calf paint before adding an outline.
 # Their original colour gradients imply volume, not garment boundaries.
 root=ET.fromstring(raw)
 shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
 union=ET.Element(root.tag,{'viewBox':'0 0 128 128','width':'1536','height':'1536'})
 for i in indices:
  part=copy.deepcopy(shapes[i]);part.attrib.pop('style',None)
  part.set('fill','#000000');part.set('stroke','none');union.append(part)
 doc=pymupdf.open(stream=ET.tostring(union),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
 mask=np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128
 paths=[]
 for c in find_contours(np.pad(mask.astype(float),1),.5):
  c=approximate_polygon(c,tolerance=.65)
  if len(c)<4:continue
  points=[f'{(x-1)/12:.4f},{(y-1)/12:.4f}' for y,x in c]
  paths.append('M'+' L'.join(points)+' Z')
 return ' '.join(paths)

EXPECTED_REGIONS.update({'1f9d1_200d_1f9af': [9, [1, 4, 5, 6]], '1f468_200d_1f9af': [9, [1, 4, 5]], '1f469_200d_1f9af': [9, [1, 4, 5, 6]], '1f9d1_200d_1f9af_200d_27a1': [9, [1, 4, 5]], '1f468_200d_1f9af_200d_27a1': [9, [1, 4, 5, 6]], '1f469_200d_1f9af_200d_27a1': [9, [1, 4, 5, 6]], '1f9d1_200d_1f9bd': [42, [1, 4, 7, 11]], '1f468_200d_1f9bd': [42, [1, 4, 7, 11]], '1f469_200d_1f9bd': [42, [1, 4, 7, 11]], '1f9d1_200d_1f9bd_200d_27a1': [42, [1, 4, 6, 7, 11]], '1f468_200d_1f9bd_200d_27a1': [42, [1, 4, 6, 7, 11]], '1f469_200d_1f9bd_200d_27a1': [42, [1, 4, 7, 11]], '1f9d1_200d_1f9bc': [19, [1, 5]], '1f468_200d_1f9bc': [19, [1, 5, 6]], '1f469_200d_1f9bc': [20, [1, 6]], '1f9d1_200d_1f9bc_200d_27a1': [19, [1, 5, 6]], '1f468_200d_1f9bc_200d_27a1': [19, [1, 5]], '1f469_200d_1f9bc_200d_27a1': [20, [1, 2, 6]]})

EXPECTED_REGIONS.update({'1f486': [7, [1, 2, 3, 4, 5, 6]], '1f486_200d_2642': [7, [1, 2, 3, 4, 5, 6]], '1f486_200d_2640': [5, [1, 2, 3, 4]], '1f487': [7, [3, 4, 5, 6]], '1f487_200d_2642': [8, [3, 5, 6, 7]], '1f487_200d_2640': [6, [3, 5]], '1f574': [19, [1, 3, 4, 9, 16, 17]], '1f9d1_200d_1fa70': [14, [1, 2, 3, 5, 7, 9, 10, 11, 12, 14]]})

RESTING_KEYS={'1f6c0', '1f9d8', '1f9d8_200d_2640', '1f6cc', '1f9d8_200d_2642'}
RECIPES.update({'1f9d8': (38, {0, 1, 2, 3, 4, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37}, {0, 3, 8, 11, 13, 14, 15, 16, 18, 19, 20, 21, 22, 23, 26, 27, 28, 32, 33, 34, 35, 36, 37}, {1, 2, 4, 6, 10, 12, 17, 24, 29, 30, 31}), '1f9d8_200d_2642': (38, {0, 1, 2, 3, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37}, {2, 7, 10, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 25, 26, 27, 30, 32, 33, 34, 35, 36, 37}, {0, 1, 3, 5, 9, 11, 16, 23, 28, 29, 31}), '1f9d8_200d_2640': (36, {0, 1, 2, 3, 5, 7, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35}, {2, 7, 10, 12, 13, 14, 15, 17, 18, 19, 20, 21, 22, 23, 27, 28, 29, 30, 31, 32, 33, 34, 35}, {0, 1, 3, 5, 9, 11, 16, 24, 25}), '1f6c0': (45, {0, 1, 2, 3, 4, 5, 6, 11, 12, 13, 14, 18, 19, 20, 21, 22, 23, 24, 26, 27, 29, 31, 33, 34, 39}, {33, 18, 3, 4, 5, 6, 27}, {2}), '1f6cc': (17, {2, 4, 8, 10, 11, 13, 14, 15, 16}, {2, 11}, {10})})
EXPECTED_REGIONS.update({'1f6c0': [19, [7]], '1f6cc': [7, [1]], '1f9d8_200d_2642': [15, [1, 2, 3, 4, 6, 7, 13, 14, 15]], '1f9d8_200d_2640': [12, [1, 2, 4, 5, 10, 11, 12]], '1f9d8': [14, [1, 2, 3, 4, 6, 7, 11, 13, 14]]})

def prepare(key):
 expected,keep,solid,skin_paths=RECIPES[key]
 source_manifest=('noto-emoji-resting-svg.json' if key in RESTING_KEYS else 'noto-emoji-mobility-svg.json' if key in MOBILITY_KEYS else 'noto-emoji-activity-extra-svg.json' if key in EXTRA_ACTIVITY_KEYS else 'noto-emoji-activity-svg.json')
 spec=json.loads((ROOT/'data/font-sources'/source_manifest).read_text())
 entry=next(e for e in spec['files'] if e['path'].endswith(f'emoji_u{key}.svg'))
 raw=(ROOT/entry['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==entry['sha256']
 masks=[];pixels=1536;stroke=.9 if key.startswith('1f9cd') or key=='1f3c3' else (1.1 if key in {'1f6b6_200d_2640','1f6b6_200d_2642_200d_27a1','1f6b6_200d_2640_200d_27a1'} else 1.3)
 if key.startswith('1f9d8'):stroke=1.5 if key.endswith('2642') else 1.6
 if key=='1f57a':stroke=1.65
 if '_1f9af' in key:stroke=.7
 for material in [False,True]:
  root=ET.fromstring(raw);parents={c:p for p in root.iter() for c in p}
  shapes=[e for e in root.iter() if e.tag.split('}')[-1] in {'path','polygon','circle','ellipse','rect','polyline','line'}]
  assert len(shapes)==expected,(key,len(shapes),expected)
  merged={};hidden=set()
  if key.startswith('1f46f'):
   leg_groups=((3,4,5),(31,32,33)) if key.endswith('2640') else ((2,3,4),(15,16,17))
   merged={group[0]:leg_union(raw,group) for group in leg_groups}
   hidden={i for group in leg_groups for i in group[1:]}
  if key.startswith('1f9d8'):
   # Join shaded upper-arm/forearm pieces before outlining: these are skin,
   # not sleeves. Preserve the source finger and elbow contour separately.
   groups=((1,12),(2,17)) if key=='1f9d8' else ((0,11),(1,16))
   merged={group[0]:leg_union(raw,group) for group in groups}
   hidden={i for group in groups for i in group[1:]}
  for i,e in enumerate(shapes):
   parent=parents.get(e);definition=False
   while parent is not None:
    if parent.tag.split('}')[-1] in {'defs','clipPath'}:definition=True
    parent=parents.get(parent)
   if definition:continue
   if i not in keep or i in hidden:parents[e].remove(e);continue
   if i in merged:e.set('d',merged[i])
   if key=='1f6cc' and i in {10,11}:
    e.set('transform','translate(40,85) scale(1.8) translate(-40,-85)')
   style=e.attrib.pop('style','');retained=';'.join(p for p in style.split(';') if p and not p.strip().startswith(('fill:','stroke:','stroke-width:')))
   if retained:e.set('style',retained)
   black=i in (skin_paths if material else solid)
   e.set('fill','#111111' if black else '#ffffff')
   if i not in solid:
    e.set('stroke',('#111111' if i in skin_paths else '#ffffff') if material else '#111111');e.set('stroke-width',str(stroke));e.set('stroke-linejoin','round');e.set('stroke-linecap','round')
   if key in MOBILITY_KEYS and e.tag.split('}')[-1]=='line':
    e.set('fill','none');e.set('stroke','#ffffff' if material else '#111111');e.set('stroke-width','.9');e.set('stroke-linecap','round')
   # Rounded ink on the rock facets keeps needle tips connected during
   # resampling. Body, rope, helmet and anatomical boundaries are unchanged.
   rock_facets=set(range(25,32)) if key.endswith('2640') else set(range(27,34))
   if key.startswith('1f9d7_') and i in rock_facets:
    e.set('stroke','#ffffff' if material else '#111111')
    e.set('stroke-width','.15');e.set('stroke-linejoin','round')
  if key.startswith('1f9d6'):
   steam_indices={'1f9d6':(32,33),'1f9d6_200d_2642':(20,21),'1f9d6_200d_2640':(21,22)}[key]
   # Retain the source inner steam curves as open wisps, compressed horizontally
   # beside the face. End the right wisp above the robe to keep it separate.
   steam_paths=['M26.1,60.84 c3.94,6.56,9.81,13.44,3.44,20.94 C21.04,92.04,9.42,90.16,4,104.31',
                'M84.71,26.12 c2.16,2.96,8.5,7.79,12.37,15.88 c2.58,5.39,4.54,11.94,2.07,17.38 c-7.45,16.36-21.45,19.36-28.78,25.86']
   for index,path in zip(steam_indices,steam_paths):
    e=shapes[index];e.set('d',path);e.set('fill','none');e.set('stroke','#ffffff' if material else '#111111');e.set('stroke-width','1.1')
    e.set('transform','translate(4,0) scale(.4,1)' if index==steam_indices[0] else 'translate(80,0) scale(.4,1)')
    e.set('stroke-width','2.5');e.set('style','opacity:1')
  root.set('width',str(pixels));root.set('height',str(pixels))
  doc=pymupdf.open(stream=ET.tostring(root),filetype='svg');pdf=pymupdf.open('pdf',doc.convert_to_pdf());pix=pdf[0].get_pixmap(alpha=False)
  masks.append(np.asarray(Image.frombytes('RGB',(pix.width,pix.height),pix.samples)).max(axis=2)<128)
 removed_specks=0
 if key.startswith('1f9cd'):
  labels,n=ndimage.label(masks[0]);sizes=np.bincount(labels.ravel())
  specks=np.isin(labels,[i for i in range(1,n+1) if sizes[i]<4])
  removed_specks=int(specks.sum());masks[0]&=~specks
 removed=0
 if True:
  holes,n=ndimage.label(ndimage.binary_fill_holes(masks[0])&~masks[0]);sizes=np.bincount(holes.ravel())
  tiny=np.isin(holes,[i for i in range(1,n+1) if sizes[i]<4]);clean=masks[0]|tiny
  if same_features(masks[0],clean):removed=int(tiny.sum());masks[0]=clean
 seed=int.from_bytes(hashlib.sha256(key.encode()).digest()[:4],'big')
 settings=Settings(strength=1.7,seed=seed,pressure=.025 if key=='1f9cd_200d_2640' else .1,taper=0,bend=.0005 if key=='1f9cd_200d_2640' else (.001 if key.startswith('1f9cd') else .012))
 if key=='1f9d8_200d_2640' or key in {'1f57a','1f46f'} or key.startswith('1f9d7_'):settings=Settings(strength=1.7,seed=seed,pressure=.025,taper=0,bend=.001)
 image,report=translate(masks[0],settings)
 assert report["appliedStrength"]>0 and not report["fallback"],key
 ink=np.asarray(image)<128
 removed_after=0
 if True:
  holes,n=ndimage.label(ndimage.binary_fill_holes(ink)&~ink);sizes=np.bincount(holes.ravel())
  tiny=np.isin(holes,[i for i in range(1,n+1) if sizes[i]<4]);clean=ink|tiny
  if same_features(ink,clean):removed_after=int(tiny.sum());ink=clean
 white=ndimage.binary_fill_holes(ink)
 material=np.pad(masks[1],report['padding']);labels,n=ndimage.label(white&~ink);sizes=np.bincount(labels.ravel());overlaps=np.bincount(labels[material],minlength=n+1)
 selected=[i for i in range(1,n+1) if sizes[i]>=32 and overlaps[i]/sizes[i]>.5]
 # Optical prototype: inspect and pin the resulting regions before integration.
 interior=np.isin(labels,selected);excluded=(labels!=0)&~interior
 skin=ndimage.binary_dilation(interior,iterations=3)&white&~excluded
 # The sleeping source exposes only a small face above the blanket.
 assert selected and skin.sum()>(4000 if key=='1f6cc' else 5000) and not (skin&excluded).any()
 report.update(removedRasterSpeckPixels=removed_specks,removedTranslatedPinholePixels=removed_after,removedRasterPinholePixels=removed,source=entry,sourcePixels=pixels,svgStrokeWidth=stroke,enclosedRegions=n,skinRegions=selected,skinPaths=sorted(skin_paths),keptPaths=sorted(keep),solidInkPaths=sorted(solid),skinPixels=int(skin.sum()),programSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),penTranslateSha256=hashlib.sha256((ROOT/'tools/font/pen_translate.py').read_bytes()).hexdigest())
 return (white,skin,ink),report


RECIPES={"1f6cc":RECIPES["1f6cc"]}
def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--keys',nargs='*');parser.add_argument('--strict',action='store_true');args=parser.parse_args()
 active={k:v for k,v in RECIPES.items() if not args.keys or k in args.keys}
 from build_emoji import outline
 out=ROOT/'output/font-review/pen-translation';record_path=out/'sleeping-optics-svg-prototype.json'
 records=[r for r in json.loads(record_path.read_text()) if r['key'] not in active] if record_path.exists() else []
 for base in sorted({key.split('_')[0] for key in active}):
  keys=[k for k in active if k.split('_')[0]==base];sheet=Image.new('RGB',(350*len(keys),430),'#f5f2eb');draw=ImageDraw.Draw(sheet)
  for j,key in enumerate(keys):
   (white,skin,ink),r=prepare(key);ys,xs=np.nonzero(white);factor=760/max(np.ptp(xs)+1,np.ptp(ys)+1);glyph=outline(ink,(xs.min(),ys.min(),factor))
   r.update(key=key,compiledContours=glyph.numberOfContours,topologyAccepted=glyph.numberOfContours==r['sourceComponents']+r['sourceHoles'],treatmentAccepted=r['appliedStrength']>0 and not r['fallback'])
   rgb=np.full((*ink.shape,3),255,dtype='uint8');rgb[skin]=(171,129,90);rgb[ink]=17
   tile=Image.fromarray(rgb);tile.thumbnail((330,330));sheet.paste(tile,(j*350,0))
   draw.text((j*350+4,335),key,fill='black',font=ImageFont.load_default(size=15))
   draw.text((j*350+4,360),f'{r["appliedStrength"]:.3f}; contours {glyph.numberOfContours}/{r["sourceComponents"]+r["sourceHoles"]}',fill='black',font=ImageFont.load_default(size=15))
   draw.text((j*350+4,385),f'Skin regions {len(r["skinRegions"])}/{r["enclosedRegions"]}',fill='black',font=ImageFont.load_default(size=14))
   records.append(r)
  sheet.save(out/f'sleeping-optics-svg-{base}-prototype.png')
 (out/'sleeping-optics-svg-prototype.json').write_text(json.dumps(records,indent=2,ensure_ascii=False)+'\n')
 failures=[r['key'] for r in records if not (r['topologyAccepted'] and r['treatmentAccepted'])]
 print(f'{len(records)-len(failures)} / {len(records)} drawings preserve treatment and compiled contours')
 if args.strict:assert not failures,failures
if __name__=='__main__':main()
