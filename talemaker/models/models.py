from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks


def visual_question_answering(image_file, qestion, language='en'):
  model_id = 'damo/mplug_visual-question-answering_coco_large_en'
  if language == 'en': # English model
    model_id = 'damo/mplug_visual-question-answering_coco_large_en'
  elif language == 'zh': # Chinese model
    model_id = 'damo/mplug_visual-question-answering_coco_base_zh'
    
  input_vqa = {
      'image': f'{image_file}',
      'question': f"{qestion}",
  }

  pipeline_vqa = pipeline(Tasks.visual_question_answering, model=model_id)
  return pipeline_vqa(input_vqa)

def image_captioning(image_file, language='en'):
  model_id = 'damo/mplug_image-captioning_coco_large_en'
  if language == 'en':
    model_id = 'damo/mplug_image-captioning_coco_large_en'
  elif language == 'zh':
    model_id = 'damo/mplug_image-captioning_coco_base_zh'
  pipeline_caption = pipeline(Tasks.image_captioning, model=model_id)
  return pipeline_caption(image_file) 

if __name__ == '__main__':
  image_captioning("1129-181154-17210258201808.jpg")
  pass