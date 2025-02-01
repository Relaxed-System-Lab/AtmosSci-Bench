1.19. Derive an expression for the altitude variation of the pressure change $\delta p$ that occurs when an atmosphere with constant lapse rate is subjected to a height independent temperature change $\delta T$ while surface pressure remains constant. At what height is the magnitude of the pressure change a maximum if the lapse rate is $6.5 \mathrm{~K} \mathrm{~km}^{-1}, T_{0}=300$, and $\delta T=2 \mathrm{~K}$ ?

Solution: From Problem 1.16:

$$
\left(\frac{p_{1}}{p_{0}}\right)=\left(\frac{T_{0}-\gamma Z}{T_{0}}\right)^{\frac{g_{0}}{R_{\gamma}}}
$$

and thus

$$
\left(\frac{p_{1}+\delta p}{p_{0}}\right)=\left(1-\frac{\gamma Z}{T_{0}+\delta T}\right)^{\frac{g_{0}}{R \gamma}}
$$

or

$$
\left(\frac{\delta p}{p_{0}}\right)=\left(1-\frac{\gamma Z}{T_{0}+\delta T}\right)^{\frac{g_{0}}{R \gamma}}-\left(1-\frac{\gamma Z}{T_{0}}\right)^{\frac{g_{0}}{R \gamma}}
$$

To find the height at which $\delta p$ is a maximum, we evaluate $\partial(\delta p) / \partial Z$ in the preceding expression and set the result to zero. Letting $\varepsilon \equiv\left(g_{0} / R \gamma\right)-1$ the result becomes

$$
\frac{1}{T_{0}+\delta T}\left(1-\frac{\gamma Z}{T_{0}+\delta T}\right)^{\varepsilon}=\frac{1}{T_{0}}\left(1-\frac{\gamma Z}{T_{0}}\right)^{\varepsilon}
$$

which can be simplified to the form

$$
\left(\frac{T_{0}}{T_{0}+\delta T}\right)^{\frac{1}{\varepsilon}}\left(1-\frac{\gamma Z}{T_{0}+\delta T}\right)=\left(1-\frac{\gamma Z}{T_{0}}\right)
$$

When solved for Z, this gives

$$
Z_{\max }=\frac{T_{0}}{\gamma}\left[1-\left(\frac{T_{0}}{T_{0}+\delta T}\right)^{\frac{1}{\varepsilon}}\right] /\left[1-\left(\frac{T_{0}}{T_{0}+\delta T}\right)^{1+\frac{1}{\varepsilon}}\right]=8.806 \mathrm{~km}
$$
