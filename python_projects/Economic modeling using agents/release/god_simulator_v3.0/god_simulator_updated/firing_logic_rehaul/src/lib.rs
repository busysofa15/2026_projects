use pyo3::prelude::*;
use numpy::PyReadwriteArray1;

#[pyfunction]
fn process_firings_rust<'py>(
    py: Python<'py>,
    mut employer_id_py: PyReadwriteArray1<'py, i32>,
    business_ids: Vec<i32>,
    fires_count: Vec<i32>,
    unemployed_id: i32,
) -> PyResult<()> {
    let employer_ids = employer_id_py.as_slice_mut()?;

    for (&biz_id, &num_to_fire) in business_ids.iter().zip(fires_count.iter()) {
        if num_to_fire <= 0 {
            continue;
        }

        let mut fired_so_far = 0;

        for emp_id in employer_ids.iter_mut() {
            if *emp_id == biz_id {
                *emp_id = unemployed_id;
                fired_so_far += 1;

                if fired_so_far >= num_to_fire {
                    break;
                }
            }
        }
    }

    Ok(())
}

/// This registers the function into the Python module.
/// The function name HERE must match the `name = "..."` inside your Cargo.toml!
#[pymodule]
fn firing_logic_rehaul(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(process_firings_rust, m)?)?;
    Ok(())
}