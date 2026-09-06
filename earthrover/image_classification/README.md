# AI Robot: Image Classification

The robot streams what the camera sees with the model's guess written over it,
and speaks the name of whatever it recognises.

**The control panel runs `image_recog_cv2.py`.**

## Code files

### `image_recog_cv2.py`
Captures frames, runs them through a MobileNet classifier on the TensorFlow
Lite interpreter, overlays the label and confidence, and streams the result
over LAN with FLASK. Speech is handled by the speaker code in `../speaker`.

### `master.py`
Started by the control panel, not by hand. It stops whatever else is holding
the camera, launches `image_recog_cv2.py`, and stops it again when the button
is switched off.

### `web/`
The page the control panel opens, and the small PHP endpoints behind it.

## The model

The model and its labels live in the `all_models` directory beside
`earthrover`, not here. With a Coral USB Accelerator attached the `_edgetpu`
build of the model is used automatically; without one the same code runs on
the CPU. `util.py` decides, and the control panel shows which backend is in
use next to "AI Robotics".
