import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  static targets = ["title", "summary", "previewTitle", "previewSummary"]

  update() {
    if (this.hasTitleTarget && this.hasPreviewTitleTarget) {
      this.previewTitleTarget.textContent = this.titleTarget.value || "제목을 입력하세요"
    }
    if (this.hasSummaryTarget && this.hasPreviewSummaryTarget) {
      const text = this.summaryTarget.value || "요약 내용이 여기에 표시됩니다"
      this.previewSummaryTarget.textContent = text.substring(0, 150)
    }
  }
}
