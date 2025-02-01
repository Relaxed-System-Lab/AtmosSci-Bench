6. (i) A typical hurricane at, say, $30^{\circ}$ latitude may have low-level winds of $50 \mathrm{~ms}^{-1}$ at a radius of 50 km from its center: do you expect this flow to be geostrophic?
(ii) Two weather stations near $45^{\circ} \mathrm{N}$ are 400 km apart, one exactly to the northeast of the other. At both locations, the 500 hPa wind is exactly southerly at $30 \mathrm{~ms}^{-1}$. At the north-eastern station, the height of the 500 hPa surface is 5510 m ; what is the height of this surface at the other station?

ANSWER:
(i) At $30^{\circ} \mathrm{N}$, the Coriolis parameter is $f=2 \Omega \sin 30^{\circ}=\Omega=7.27 \times 10^{-5} \mathrm{~s}^{-1}$, so the Rossby number for a hurricane with winds $50 \mathrm{~ms}^{-1}$ at a radius of 50 km is

$$
R=\frac{50}{7.27 \times 10^{-5} \times 5 \times 10^{4}} \simeq 13.8
$$

This number is not small, so the flow is not expected to be geostrophic.

(ii) Assuming geostrophic balance (and using our standard notation, in pressure coordinates)

$$
(u, v)=\frac{g}{f}\left(-\frac{\partial z}{\partial y}, \frac{\partial z}{\partial x}\right) .
$$

Given that the flow is $30 \mathrm{~ms}^{-1}$ southerly, the 500 hPa height gradient is

$$
\begin{aligned}
\left(\frac{\partial z}{\partial x}, \frac{\partial z}{\partial y}\right) & =\left(\frac{f v}{g},-\frac{f u}{g}\right) \\
& =\left(\frac{1.03 \times 10^{-4} \times 30}{9.81}, 0\right)=\left(3.15 \times 10^{-4}, 0\right) \text { [dimensionless]. }
\end{aligned}
$$

If $z_{e}$ and $z_{w}$ are the 500 hPa heights at the eastern and western stations, respectively, then, assuming the components of the vector separating the two stations, $\delta x=x_{e}-x_{w}=400 / \sqrt{2} \mathrm{~m}$ and $\delta y=y_{e}-y_{w}=$ $400 / \sqrt{2} \mathrm{~m}$, are small enough,

$$
\begin{aligned}
\delta z & =z_{e}-z_{w}=\frac{\partial z}{\partial x} \delta x+\frac{\partial z}{\partial y} \delta y=\frac{\partial z}{\partial x} \delta x \\
& =3.15 \times 10^{-4} \times \frac{4 \times 10^{5}}{\sqrt{2}}=89 \mathrm{~m} .
\end{aligned}
$$

Therefore the height at the western station is $5510-89=5421 \mathrm{~m}$.