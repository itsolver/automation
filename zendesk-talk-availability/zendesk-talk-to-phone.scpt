FasdUAS 1.101.10   ��   ��    k             l    	 ����  I    	���� 
�� .sysonotfnull��� ��� TEXT��    �� 	 

�� 
appr 	 m       �   2 Z e n d e s k   T a l k   a v a i l a b i l i t y 
 �� ��
�� 
subt  m       �    S e t   t o   p h o n e��  ��  ��     ��  l  
  ����  I  
 �� ��
�� .sysoexecTEXT���     TEXT  m   
    �   # ! / b i n / s h 
 # Y o u r   Z e n d e s k   U R L   h a s   t w o   p a r t s :   a   s u b d o m a i n   n a m e   y o u   c h o s e   w h e n   y o u   s e t   u p   y o u r   a c c o u n t ,   f o l l o w e d   b y   z e n d e s k . c o m   ( f o r   e x a m p l e :   m y c o m p a n y . z e n d e s k . c o m ) . 
 # Y o u r   Z e n d e s k   U s e r   I D   i s   f o u n d   i n   A g e n t   P r o f i l e   U R L . 
 # R e q u i r e s   Z e n d e s k   A P I   T o k e n   A c c e s s 
 # A d d   A c t i v a t e   A P I   T o k e n   t o   K e y c h a i n   a s   a   n e w   P a s s w o r d   i t e m ,   s e t   a c c o u n t   n a m e   t o   y o u r   $ z e n d e s k U s e r n a m e   +   ' / t o k e n ' ,   e . g .   ' s u e @ e x a m p l e . c o m / t o k e n ' . 
 # # # # # 
 # E n t e r   y o u r   c r e d e n t i a l s   h e r e : 
 z e n d e s k S u b d o m a i n = i t s o l v e r 
 z e n d e s k U s e r I D = 3 6 3 4 8 7 3 9 6 
 z e n d e s k U s e r n a m e = a n g u s @ i t s o l v e r . n e t / t o k e n 
 g e t _ p w   ( )   { 
 s e c u r i t y   2 > & 1   > / d e v / n u l l   f i n d - g e n e r i c - p a s s w o r d   - g a   $ z e n d e s k U s e r n a m e / t o k e n | r u b y   - e   ' p r i n t   $ 1   i f   S T D I N . g e t s   = ~   / ^ p a s s w o r d :   " ( . * ) " $ / ' 
 } 
 c u r l   h t t p s : / / $ z e n d e s k S u b d o m a i n . z e n d e s k . c o m / a p i / v 2 / c h a n n e l s / v o i c e / a v a i l a b i l i t i e s / $ z e n d e s k U s e r I D . j s o n   - H   " C o n t e n t - T y p e :   a p p l i c a t i o n / j s o n "   - d   ' { " a v a i l a b i l i t y " :   { " v i a " :   " p h o n e " ,   " a v a i l a b l e " :   t r u e } } '   - v   - u   $ z e n d e s k U s e r n a m e / t o k e n : $ ( g e t _ p w )   - X   P U T��  ��  ��  ��       ��  ��    ��
�� .aevtoappnull  �   � ****  �� ����  ��
�� .aevtoappnull  �   � ****  k             ����  ��  ��       �� �� ���� ��
�� 
appr
�� 
subt�� 
�� .sysonotfnull��� ��� TEXT
�� .sysoexecTEXT���     TEXT�� *����� O�j ascr  ��ޭ