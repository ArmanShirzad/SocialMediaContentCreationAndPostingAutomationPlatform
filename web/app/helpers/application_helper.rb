module ApplicationHelper
  include Pagy::Frontend

  def sidebar_link(label, path, icon)
    active = current_page?(path)
    base = "flex items-center gap-2.5 px-3 py-2.5 rounded-md text-sm font-medium transition-colors"
    classes = active ? "#{base} bg-surface text-text" : "#{base} text-text-muted hover:bg-surface hover:text-text"

    link_to path, class: classes do
      sidebar_icon(icon) + content_tag(:span, label)
    end
  end

  def sidebar_icon(name)
    icons = {
      "grid" => '<svg class="w-[18px] h-[18px] opacity-70" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>',
      "file" => '<svg class="w-[18px] h-[18px] opacity-70" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
      "layout" => '<svg class="w-[18px] h-[18px] opacity-70" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="3" x2="9" y2="21"/></svg>',
      "search" => '<svg class="w-[18px] h-[18px] opacity-70" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
      "settings" => '<svg class="w-[18px] h-[18px] opacity-70" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>'
    }
    icons[name]&.html_safe || ""
  end

  def status_badge(article)
    case article.status
    when :completed
      content_tag(:span, class: "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-success-muted text-success") do
        content_tag(:span, "", class: "w-1.5 h-1.5 rounded-full bg-current") + "완료"
      end
    when :partial
      content_tag(:span, class: "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-warning-muted text-warning") do
        content_tag(:span, "", class: "w-1.5 h-1.5 rounded-full bg-current") + "진행중"
      end
    when :pending
      content_tag(:span, class: "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-[rgba(161,161,170,0.12)] text-text-muted") do
        content_tag(:span, "", class: "w-1.5 h-1.5 rounded-full bg-current") + "대기중"
      end
    end
  end

  def platform_icon(posted, label)
    if posted
      content_tag(:span, label, class: "w-7 h-7 rounded-md flex items-center justify-center text-[13px] font-bold font-mono bg-success-muted text-success")
    else
      content_tag(:span, label, class: "w-7 h-7 rounded-md flex items-center justify-center text-[13px] font-bold font-mono bg-[rgba(161,161,170,0.1)] text-text-dim")
    end
  end
end
