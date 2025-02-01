Determine the radii of curvature for the trajectories of air parcels located 500 km to the east, north, south, and west of the center of a circular low-pressure system, respectively. The system is moving eastward at $15 \mathrm{~m} \mathrm{~s}^{-1}$. Assume geostrophic flow with a uniform tangential wind speed of $15 \mathrm{~m} \mathrm{~s}^{-1}$.
Then determine the normal gradient wind speeds for the four air parcels using the radii of curvature computed. Compare these speeds with the geostrophic speed. (Let $f=10^{-4} \mathrm{~s}^{-1}$.) Use the gradient wind speeds calculated here to recompute the radii of curvature for the four air parcels Use these new estimates of the radii of curvature to recompute the gradient wind speeds for the four air parcels. What fractional error is made in the radii of curvature by using the geostrophic wind approximation in this case? (Note that further iterations could be carried out, but would rapidly converge.)


Solution:
Step 1:
From (3.24) $R_{s}=R_{t}(1-c \cos \gamma / V)$, where $c=V=15 \mathrm{~m} / \mathrm{s}$, and $R_{s}=500 \mathrm{~km}$. Thus,

$$
\begin{array}{ll}
\text { North of center } & R_{t}=R_{S} / 2=250 \mathrm{~km}(\gamma=\pi) \\
\text { West of center } & R_{t}=R_{S}=500 \mathrm{~km} \quad(\gamma=3 \pi / 2) \\
\text { South of center } & R_{t} \rightarrow \infty \quad(\gamma=0) \\
\text { East of center } & R_{t}=R_{s}=500 \mathrm{~km} \quad(\gamma=\pi / 2)
\end{array}
$$

Step 2: Gradient wind speed for normal low is given by

$$
V_{g r a d}=-\left(\frac{f R_{t}}{2}\right)+\left[\left(\frac{f R_{t}}{2}\right)^{2}+f R_{t} V_{g}\right]^{1 / 2}
$$

Using the radii of curvature from Step 1, we obtain

$$
\begin{aligned}
& \text { North of center } \quad V_{g r a d}=10.5 \mathrm{~m} / \mathrm{s} \\
& \text { West of center } \quad V_{g r a d}=12.1 \mathrm{~m} / \mathrm{s} \\
& \text { South of center } V_{g r a d}=15 \mathrm{~m} / \mathrm{s} \\
& \text { East of center } \quad V_{\text {grad }}=12.1 \mathrm{~m} / \mathrm{s}
\end{aligned}
$$

Substituting these values of gradient wind into the formula of Step 1, we find that only the trajectory curvature north of the center changes: North of center $R_{t}=R_{s} /(1+15 / 10.5)=206 \mathrm{~km}$. Plugging this value into the gradient wind formula, we find North of center $V_{\text {grad }}=10.07 \mathrm{~m} / \mathrm{s}$, which is about a $4 \%$ decrease.
