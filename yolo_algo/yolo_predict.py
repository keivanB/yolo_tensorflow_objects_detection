import tensorflow as tf
from keras import backend as K
from keras.models import load_model, Model
from .utils.yolo_utils import read_classes, read_anchors, generate_colors, preprocess_image, draw_boxes, scale_boxes
from .utils.keras_yolo import yolo_head, yolo_boxes_to_corners, preprocess_true_boxes, yolo_loss, yolo_body
from .yolo_boxes_filtering import yolo_eval
from .utils.timer import Timer


def load_keras_model(sess, model_filename, classes_filename, anchors_filename):
    K.set_session(sess)
    class_names = read_classes(classes_filename)
    anchors = read_anchors(anchors_filename)
    image_shape = (720., 1280.)
    yolo_model = load_model(model_filename)
    yolo_outputs = yolo_head(yolo_model.output, anchors, len(class_names))
    scores, boxes, classes = yolo_eval(yolo_outputs, image_shape)
    return yolo_model, class_names, scores, boxes, classes

def predict(sess, yolo_model, class_names, scores, boxes, classes, image_file ):
    """
    Runs the graph stored in "sess" to predict boxes for "image_file". Prints and plots the preditions.

    Arguments:
    sess -- your tensorflow/Keras session containing the YOLO graph
    image_file -- name of an image stored in the "images" folder.

    Returns:
    out_scores -- tensor of shape (None, ), scores of the predicted boxes
    out_boxes -- tensor of shape (None, 4), coordinates of the predicted boxes
    out_classes -- tensor of shape (None, ), class index of the predicted boxes

    Note: "None" actually represents the number of predicted boxes, it varies between 0 and max_boxes.
    """

    # start timer
    timer = Timer()
    timer.tic()

    # Preprocess your image
    image, image_data = preprocess_image(image_file, model_image_size = (608, 608))

    # Run the session with the correct tensors and choose the correct placeholders in the feed_dict.
    # You'll need to use feed_dict={yolo_model.input: ... , K.learning_phase(): 0})
    out_scores, out_boxes, out_classes = sess.run([ scores, boxes, classes ], feed_dict={yolo_model.input: image_data, K.learning_phase(): 0})

    # measure processing_time
    processing_time = timer.toc(average=False)

    # Print predictions info
    print('Found {} boxes for {}'.format(len(out_boxes), image_file))
    # Generate colors for drawing bounding boxes.
    colors = generate_colors(class_names)
    # Draw bounding boxes on the image file
    draw_boxes(image, out_scores, out_boxes, out_classes, class_names, colors)

    # return annotated image and detected objects
    return image, out_scores, out_boxes, out_classes, processing_time