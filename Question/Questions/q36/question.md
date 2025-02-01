1. Consider an ocean of uniform density $\rho_{\text {ref }}=1000 \mathrm{~kg} \mathrm{~m}^{-3}$.
(a) From the hydrostatic relationship, determine the pressure at a depth of 1 km and at 5 km . Express your answer in units of atmospheric surface pressure, $p_{s}=1000 \mathrm{mbar}=10^{5} \mathrm{~Pa}$.

(b) Given that the heat content of an elementary mass dm of dry air at temperature $T$ is $c_{p} T d m$ (where $c_{p}$ is the specific heat of air at constant pressure), find a relationship for, and evaluate, the (vertically integrated) heat capacity (heat content per degree Kelvin) of the atmosphere per unit horizontal area. Find how deep an ocean would have to be in order to have the same heat capacity per unit horizontal area.


ANSWER:
(a) Hydrostatic balance is

$$
\frac{\partial p}{\partial z}=-g \rho
$$

whence, integrating from depth $d(z=-d)$ to the surface $(z=h)$,

$$
p(-d)=p(h)+g \rho(d+h)
$$

where $\rho$ is the constant density. Since at a depth of a km or so, $d+h \simeq d$ we may write:

$$
\begin{aligned}
& p(-1 \mathrm{~km})=\left(1+\frac{9.81 \mathrm{~m}^{2} \mathrm{~s}^{-1} \times 10^{3} \mathrm{~kg} \mathrm{~m}^{-3} \times 10^{3} \mathrm{~m}}{10^{5} \mathrm{~Pa}}\right) p_{s} \simeq 99 p_{s} \\
& p(-5 \mathrm{~km})=\left(1+\frac{9.81 \mathrm{~m}^{2} \mathrm{~s}^{-1} \times 10^{3} \mathrm{~kg} \mathrm{~m}^{-3} \times 5 \times 10^{3} \mathrm{~m}}{10^{5} \mathrm{~Pa}}\right) p_{s} \simeq 491 p_{s}
\end{aligned}
$$

(b) If the heat content per unit mass is $c_{p} T d m$, the heat capacity per unit mass is $c_{p} d m$. Hence the heat content of a vertically integrated column, per unit horizontal area, is

$$
\int_{0}^{\infty} c_{p} \rho d z=-\frac{c_{p}}{g} \int_{0}^{\infty} \frac{\partial p}{\partial z} d z=c_{p} \frac{p(0)}{g},
$$

assuming hydrostatic balance, where $p(0)$ is surface pressure $=1000 \mathrm{hPa}$ $=10^{5} \mathrm{~Pa}$, since $p(\infty)=0$. Therefore the vertically integrated heat capacity of the atmosphere is

$$
\frac{1004 \times 10^{5}}{9.81}=1.02 \times 10^{7} \mathrm{JK} \mathrm{~m}^{-2}
$$

The heat capacity per unit area of an ocean of depth $D$ is $c_{p} \rho D$, where $c_{p}=4187 \mathrm{JK} \mathrm{kg}^{-1}$ and $\rho=1000 \mathrm{~kg} \mathrm{~m}^{-3}$ of course are the values for water. For such an ocean to have the same heat capacity as the atmosphere,

$$
c_{p} \rho D=1.02 \times 10^{7} \mathrm{JK}^{-1} \mathrm{~m}^{-2}
$$

so

$$
D=\frac{1.02 \times 10^{7}}{4187 \times 1000}=2.44 \mathrm{~m}
$$

This is very shallow! So, a real ocean of depth (say) 4 km has 4000/2.44= 1639 times the heat capacity of the atmosphere.