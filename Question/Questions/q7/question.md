2. A horizontal pipe is made of forged steel. The pipe diameter is 400 mm . Room temperature water ( $23^{\circ} \mathrm{C}, \rho=997.45 \mathrm{~kg} / \mathrm{m}^{3}$ ) is transported for 500 m in the pipe, with a pressure drop of 100,000 Pa over this length. What is the flow rate in the pipe?
![](https://cdn.mathpix.com/cropped/2024_12_06_b79d610f0ffcf56a3450g-08.jpg?height=901&width=1434&top_left_y=492&top_left_x=431)

Figure 2

## Solution:

Given data:
Pipe diameter: $d=400 \mathrm{~mm}=0.4 \mathrm{~m}$
Pipe length: $d=500 \mathrm{~m}$
Pressure drop: $\Delta P=100,000 \mathrm{~Pa}$
Fluid density: $\rho=997.45 \mathrm{~kg} / \mathrm{m}^{3}$
Dynamic viscosity: $\mu=0.9321 \mathrm{mPa} \cdot \mathrm{s} \approx 0.001 \mathrm{~Pa} \cdot \mathrm{~s}$
(You can search it online, here's an example, https://wiki.anton-paar.com/en/water/)
Pipe roughness: $\varepsilon=0.025$ (From Moody chart for forged steel)
Solution steps:

1. Compute the relative roughness

$$
\frac{\varepsilon}{d}=\frac{0.025 \mathrm{~mm}}{400 \mathrm{~mm}}=0.0000625
$$

2. Calculate the Reynolds number

$$
R e=\frac{\rho \cdot V \cdot d}{\mu}=\frac{997.45 \cdot 0.634 \cdot 0.4}{0.001}=252,803
$$

3. Use the Darcy-Weisbach equation

$$
\Delta P=f \cdot \frac{L}{d} \cdot \frac{\rho V^{2}}{2}
$$

$$
f \cdot V^{2}=0.1604
$$

4. Recalculate the velocity $(V)$ using the refined friction facto
(I didn't show the iteration steps here. You can check the last lecture video, in-class exercise 2 . The process is well-stated)

$$
\begin{gathered}
f=0.01495 \\
f \cdot V^{2}=0.1604 \\
V=3.28 \mathrm{~m} / \mathrm{s} \\
Q=V \cdot A=V \cdot \frac{\pi d^{2}}{4}=0.412 \mathrm{~m}^{3} / \mathrm{s}
\end{gathered}
$$

(Show the clear solution process will get you full marks)
