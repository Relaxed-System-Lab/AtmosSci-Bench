3. Consider the thermal balance of Jupiter. You will need the following information about Jupiter: mean planetary radius $=69500 \mathrm{~km}$; mean radius of orbit around the Sun $=5.19$ A.U. (where 1A.U. is the mean radius of the Earth's orbit); planetary albedo $=0.51$.
(a) Assuming a balance between incoming and outgoing radiation, calculate the emission temperature for Jupiter.

(b) In fact, Jupiter has an internal heat source resulting from continued planetary contraction. Using the conventional definition of emission temperature $T_{e}$,
$\sigma T_{e}^{4}=$ (outgoing flux of planetary radiation per unit surface area)
the measured emission temperature of Jupiter is 130K. Calculate the magnitude of Jupiter's internal heat source.

(c) It is believed that the source of $Q$ on Jupiter is the release of gravitational potential energy by a slow contraction of the planet. On the simplest assumption that Jupiter is of uniform density and remains so as it contracts, calculate the annual change in its radius $a_{\text {jup }}$ required to produce your value of $Q$. (Only one half of the released gravitational energy is convertible to heat, the remainder appearing as the additional kinetic energy required to preserve the angular momentum of the planet.)

ANSWER:
(a) Solar flux at earth orbit $S_{0}=1367 \mathrm{Wm}^{-2}$, so solar flux at Jupiter's orbit is

$$
S_{J}=S_{0}\left(\frac{\text { mean radius of earth's orbit }}{\text { mean radius of Jupiter's orbit }}\right)^{2}=\frac{1367}{(5.19)^{2}}=50.75 \mathrm{Wm}^{-2}
$$

Given a Jupiter albedo $\alpha_{J}=0.51$,

$$
\text { net solar input }=S_{J}\left(1-\alpha_{J}\right) \pi a_{J}^{2}=3.77 \times 10^{17} \mathrm{~W}
$$

Assuming blackbody radiation at temperature $T_{J}$,

$$
\text { net thermal emission }=4 \pi a_{J}^{2} \sigma T_{J}^{4} \text {. }
$$

Assuming these balance gives

$$
T_{J}=\left[\frac{\left(1-\alpha_{J}\right) S_{J}}{4 \sigma}\right]^{\frac{1}{4}}=102.3 \mathrm{~K}
$$

(b) Observations show actual emission temperature is $T_{J}^{a c t u a l}=130 \mathrm{~K}$, i.e.
Therefore, if the net internal heat source is $H$,

$$
\begin{aligned}
H & =(\text { net thermal emission })-(\text { net solar input }) \\
& =\pi a_{J}^{2}\left[4 \sigma\left(T_{J}^{a c t u a l}\right)^{4}-S_{J}\left(1-\alpha_{J}\right)\right] \\
& =6.06 \times 10^{17} \mathrm{~W} .
\end{aligned}
$$

(c) [A uniform sphere of mass $M$ and radius a has a gravitational potential energy of $-\frac{3}{5} G \frac{M^{2}}{a}$ where $G$ is the gravitational constant $=6.7 \times 10^{-11} \mathrm{~kg}^{-1} \mathrm{~m}^{3} \mathrm{~s}^{-2}$. The mass of Jupiter is $2 \times 10^{27} \mathrm{~kg}$ and its radius is $a_{j u p}=7.1 \times 10^{7} \mathrm{~m}$.]
Expressing what we are told in mathematics we have:

$$
\frac{1}{2} \frac{\partial}{\partial t}\left(-\frac{3}{5} G \frac{M^{2}}{a}\right)=4 \pi a^{2} Q=H
$$

and so, noting that $\frac{\partial}{\partial t}\left(-\frac{1}{a}\right)=\frac{1}{a^{2}} \frac{\partial}{\partial t} a$ and rearranging we find

$$
\frac{\partial}{\partial t} a=\frac{40 \pi}{3} \frac{a^{2}}{G M^{2}} H
$$

Inserting numbers we have

$$
\begin{aligned}
\frac{\partial}{\partial t} a & =\frac{40 \pi}{3} \frac{\left(7.1 \times 10^{7} \mathrm{~m}\right)^{2}}{6.7 \times 10^{-11} \mathrm{~kg}^{-1} \mathrm{~m}^{3} \mathrm{~s}^{-2} \times\left(2 \times 10^{27} \mathrm{~kg}\right)^{2}} \times 6.06 \times 10^{17} \mathrm{~J} \mathrm{~s}^{-1} \\
& =4.8 \times 10^{-10} \mathrm{~m} \mathrm{~s}^{-1}=1.5 \times 10^{-2} \mathrm{~m} \text { per year! }
\end{aligned}
$$