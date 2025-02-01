3.22. The divergence of the horizontal wind at various pressure levels above a given station is shown in the following table.

| Pressure $(\mathbf{h P a})$ | $\boldsymbol{\nabla} \cdot \mathbf{V} \mathbf{( \times \mathbf { 1 0 } ^ { - \mathbf { 5 } } \mathbf { s } ^ { \mathbf { - 1 } } )}$ |
| :---: | :---: |
| 1000 | +0.9 |
| 850 | +0.6 |
| 700 | +0.3 |
| 500 | 0.0 |
| 300 | -0.6 |
| 100 | -1.0 |

Compute the vertical velocity at each level assuming an isothermal atmosphere with temperature 260 K and letting $w=0$ at 1000 hPa .

Solution: From eq. (3.38): $\omega\left(p_{1}\right)=\omega\left(p_{0}\right)+\left(p_{0}-p_{1}\right)\langle\nabla \cdot \mathbf{V}\rangle$, where in this case the vertical average of the divergence in each layer must be estimated from averaging the top and bottom values: $\langle\nabla \cdot \mathbf{V}\rangle=\frac{1}{2}\left[(\nabla \cdot \mathbf{V})_{p_{0}}+(\nabla \cdot \mathbf{V})_{p_{1}}\right]$. If $\omega(1000 \mathrm{hPa})=0$, then integrating upward gives

$$
\begin{aligned}
\omega(850 \mathrm{hPa}) & =11.25 \times 10^{-2} \mathrm{~Pa} \mathrm{~s}^{-1} \\
\omega(700 \mathrm{hPa}) & =18.00 \times 10^{-2} \mathrm{~Pa} \mathrm{~s}^{-1} \\
\omega(500 \mathrm{hPa}) & =21.00 \times 10^{-2} \mathrm{~Pa} \mathrm{~s}^{-1} \\
\omega(300 \mathrm{hPa}) & =15.00 \times 10^{-2} \mathrm{~Pa} \mathrm{~s}^{-1} \\
\omega(100 \mathrm{hPa}) & =-1.00 \times 10^{-2} \mathrm{~Pa} \mathrm{~s}^{-1}
\end{aligned}
$$

Now $w \approx-\left(\frac{R T}{g}\right)\left(\frac{\omega}{p}\right)=\left(-7.61 \times 10^{3}\right)\left(\frac{\omega}{p}\right)$. Thus, from the above expressions we estimate the vertical velocity at each level as

$$
\begin{aligned}
& w(850)=-1.0 \mathrm{~cm} \mathrm{~s}^{-1} \\
& w(700)=-2.0 \mathrm{~cm} \mathrm{~s}^{-1} \\
& w(500)=-3.3 \mathrm{~cm} \mathrm{~s}^{-1} \\
& w(300)=-3.8 \mathrm{~cm} \mathrm{~s}^{-1} \\
& w(100)=+0.8 \mathrm{~cm} \mathrm{~s}^{-1}
\end{aligned}
$$
