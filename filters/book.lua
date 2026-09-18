-- filters/book.lua
-- 1. Format Tao Te Ching verses as line blocks with proper line breaks
-- 2. Remove figure environment and captions from decorative divider images

local in_verse = false

function Pandoc(doc)
  local new_blocks = {}
  in_verse = false

  for _, block in ipairs(doc.blocks) do
    if block.t == 'Header' then
      in_verse = false
      table.insert(new_blocks, block)

    elseif block.t == 'Figure' then
      local is_divider = false
      local is_calligraphy = false
      local img_el = nil

      block:walk {
        Image = function(img)
          img_el = img
          local src = img.src or ''
          local alt = pandoc.utils.stringify(img.caption or ''):lower()
          if src:match('common%.jpg') or alt:match('divider') then
            is_divider = true
          elseif src:match('f%d%d%d%d%-01%.jpg') or alt:match('calligraphy') then
            is_calligraphy = true
          end
        end
      }

      if is_divider and img_el then
        img_el.caption = {}
        if FORMAT:match('latex') then
          table.insert(new_blocks, pandoc.RawBlock('latex', [[\begin{center}]]))
          table.insert(new_blocks, pandoc.Para({img_el}))
          table.insert(new_blocks, pandoc.RawBlock('latex', [[\end{center}]]))
        else
          table.insert(new_blocks, pandoc.Div(
            {pandoc.Para({img_el})},
            {class = 'divider', style = 'text-align: center; margin: 1.5em 0;'}
          ))
        end
      else
        if is_calligraphy then
          in_verse = true
        end
        table.insert(new_blocks, block)
      end

    elseif block.t == 'Para' then
      if in_verse then
        in_verse = false
        -- Convert soft line breaks in the verse block to distinct verse lines
        local lines = {}
        local current_line = {}
        for _, inline in ipairs(block.content) do
          if inline.t == 'SoftBreak' or inline.t == 'LineBreak' then
            table.insert(lines, current_line)
            current_line = {}
          else
            table.insert(current_line, inline)
          end
        end
        if #current_line > 0 then
          table.insert(lines, current_line)
        end

        local line_block = pandoc.LineBlock(lines)
        table.insert(new_blocks, pandoc.Div({line_block}, {class = 'verse'}))
      else
        table.insert(new_blocks, block)
      end

    else
      table.insert(new_blocks, block)
    end
  end

  doc.blocks = new_blocks
  return doc
end
