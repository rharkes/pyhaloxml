use pyo3::prelude::*;

#[pymodule]
fn pyhaloxml_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    #[pyfn(m)]
    #[pyo3(name = "point_in_polygon")]
    fn point_in_polygon(
        _py: Python,
        point: (f64, f64),
        polygon: Vec<(f64, f64)>
    ) -> PyResult<bool> {
        let mut p1x = polygon[0].0;
        let mut p1y = polygon[0].1;
        let mut p2x;
        let mut p2y;
        let mut xints = 0.0;
        let mut inside = false;
        let mut idx;
        let nvertices = polygon.len();
        for i in 0..(1 + nvertices) {
            idx = i % nvertices;
            p2x = polygon[idx].0;
            p2y = polygon[idx].1;
            if (p1y.min(p2y) < point.1) &
               (point.1 <= p1y.max(p2y)) &
               (point.0 <= p1x.max(p2x)) {
                if p1y != p2y {
                    xints = (point.1 - p1y) * (p2x - p1x) / (p2y - p1y) + p1x;
                }
                if (p1x == p2x) | (point.0 <= xints) {
                    inside = !inside;
                }
            }
            p1x = p2x;
            p1y = p2y;
        }
        Ok(inside)
    }

    Ok(())
}
