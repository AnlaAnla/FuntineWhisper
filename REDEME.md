# Whisper微调项目流程

<!-- TOC -->
* [Whisper微调项目流程](#whisper微调项目流程)
  * [1. 准备数据](#1-准备数据)
    * [音频文件](#音频文件)
<!-- TOC -->

## 1. 准备数据
### 音频文件

```html
<View>
  <Audio name="audio" value="$audio" zoom="true" hotkey="ctrl+enter"/>
  <Header value="--对照文字内容, 如果不一样在下面修改--"/>
  <Header value="$sentence" size="12"/>
  <TextArea name="transcription" toName="audio" rows="4" editable="true" maxSubmissions="1"/>
</View>

```