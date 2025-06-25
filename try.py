1. Collinear(a,c,d) & Collinear(b,c,g) & Parallel(a,b,d,g) [AlphaGeometry8(a,b,d,g,c)] => Length_a_c/Length_b_c - Length_a_d/Length_b_g
2. Collinear(b,c,e) & Collinear(b,c,g) [CollinearTransist(b,c,e,g)] => Collinear(b,e,g)
3. Collinear(a,b,f) [CollinearParallel(a,b,f)] => Parallel(a,b,b,f)
4. Parallel(a,b,b,f) & Parallel(a,b,d,g) [ParaTrans(a,b,b,f,d,g)] => Parallel(b,f,d,g)
5. Collinear(b,e,g) & Collinear(d,e,f) & Parallel(b,f,d,g) [AlphaGeometry8(b,f,g,d,e)] => Length_b_e/Length_e_f - Length_b_g/Length_d_f
6. Length_a_c/Length_b_c - Length_a_d/Length_b_g & -Length_a_d + Length_b_e & Length_a_c - Length_b_c & Length_b_e/Length_e_f - Length_b_g/Length_d_f => -Length_d_f + Length_e_f
7. -Length_d_f + Length_e_f => Length_d_f - Length_e_f

1. Collinear(a,c,d) & Collinear(b,c,g) & Parallel(a,b,d,g) [AlphaGeometry8(a,b,d,g,c)] => Length_a_c/Length_b_c - Length_a_d/Length_b_g
2. Collinear(b,c,e) & Collinear(b,c,g) [CollinearTransist(b,c,e,g)] => Collinear(b,e,g)
3. Collinear(a,b,f) [CollinearParallel(a,b,f)] => Parallel(a,b,b,f)
4. Parallel(a,b,b,f) & Parallel(a,b,d,g) [ParaTrans(a,b,b,f,d,g)] => Parallel(b,f,d,g)
5. Collinear(b,e,g) & Collinear(d,e,f) & Parallel(b,f,d,g) [AlphaGeometry8(b,f,g,d,e)] => Length_b_e/Length_e_f - Length_b_g/Length_d_f
6. -Length_a_d + Length_b_e & Length_a_c/Length_b_c - Length_a_d/Length_b_g & Length_b_e/Length_e_f - Length_b_g/Length_d_f & Length_a_c - Length_b_c => Length_d_f - Length_e_f
7. Length_d_f - Length_e_f => Length_d_f - Length_e_f