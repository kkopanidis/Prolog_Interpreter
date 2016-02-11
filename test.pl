isBoy(kostas, aged, isMale(K)).
isGirl(xrusa).
isSleeping(leuterhs).
isBoy(leuterhs).
isAwesome(leuterhs).
isBored(X):- isSleeping(X), isBoy(X).
jealous(X,Y):- loves(X,Z),loves(Y,Z).
loves(vincent,mia).
loves(lam0,mia0).
loves(X,Y):-likes(X,Y),likes(Y,X).
likes(lam,mia).
likes(mia,lam).
member(X,[X|T]).
member(X,[H|T]) :- member(X,T).
append([],L,L).
append([H|T],L2,[H|L3]):- append(T,L2,L3).
awesome([a,[t,b],c]).
s(Z):-np(X),vp(Y),append(X,Y,Z).
np(Z):-det(X),n(Y),append(X,Y,Z).
vp(Z):-v(X),np(Y),append(X,Y,Z).
vp(Z):-v(Z).
det([the]).
det([a]).
n([woman]).
n([man]).
v([shoots]).