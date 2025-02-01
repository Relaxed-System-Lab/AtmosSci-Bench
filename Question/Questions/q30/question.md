2. Using the hydrostatic equation, derive an expression for the pressure at the center of a planet in terms of its surface gravity, radius a and density $\rho$, assuming that the latter does not vary with depth. Insert values appropriate for the earth and evaluate the central pressure. [Hint: the gravity at radius $r$ is $g(r)=\frac{G m(r)}{r^{2}}$ where $m(r)$ is the mass inside a radius $r$ and $G=6.67 \times 10^{-11} \mathrm{~kg}^{-1} \mathrm{~m}^{3} \mathrm{~s}^{-2}$ is the gravitational constant. You may assume the density of rock is $2000 \mathrm{~kg} \mathrm{~m}^{-3}$.]

ANSWER:
The hydrostatic equation is

$$
\frac{\partial p}{\partial r}=-\rho(r) g(r)
$$

where the acceleration due to gravity $g(r)$ at distance $r$ is

$$
g(r)=\frac{G m(r)}{r^{2}}
$$

where $m(r)$ is the mass inside radius $r$. If the planet has a uniform density $m(r)=\frac{4}{3} \pi r^{3} \rho$

$$
\frac{\partial p}{\partial r}=-\rho G \frac{4}{3} \pi r^{3} \frac{\rho}{r^{2}}
$$

and so

$$
\int_{0}^{p_{o}} d p=-\frac{4}{3} \pi \rho^{2} G \int_{a}^{0} r d r
$$

giving

$$
p_{0}=\frac{2}{3} \pi G \rho^{2} a^{2}
$$

Noting that $M=\frac{4}{3} \pi a^{3} \rho$ is the mass of the planet and $g_{a}=\frac{M G}{a^{2}}$ is the surface gravity, then $p_{0}=\frac{1}{2} g_{a} \rho a$.
Inserting numbers for the earth we find that: $p_{0}=\frac{1}{2} 9.81 \times 2000 \times$ $6.37 \times 10^{6}=1.25 \times 10^{11} \simeq 10^{6}$ atmospheres.