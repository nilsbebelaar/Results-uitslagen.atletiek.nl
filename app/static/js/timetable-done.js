$(function () {
    function parseDone() {
        var params = new URLSearchParams(window.location.search);
        var raw = params.get('done') || '';
        var set = new Set();
        raw.split(',').forEach(function (b) {
            b = b.trim();
            if (b) set.add(b);
        });
        return set;
    }

    var doneSet = parseDone();

    function bibsParam(set) {
        return Array.from(set).sort(function (a, b) {
            if (a.length !== b.length) return a.length - b.length;
            return a < b ? -1 : (a > b ? 1 : 0);
        }).join(',');
    }

    // URLSearchParams percent-encodes commas (%2C); undo just that so bibs/done
    // stay readable in the address bar, matching the server-rendered links.
    function unescapeCommas(str) {
        return str.replace(/%2C/gi, ',');
    }

    function withDone(href, doneValue) {
        var url = new URL(href, window.location.origin);
        if (doneValue) {
            url.searchParams.set('done', doneValue);
        } else {
            url.searchParams.delete('done');
        }
        return unescapeCommas(url.pathname + url.search);
    }

    function updateUrlBar() {
        var url = new URL(window.location.href);
        var doneValue = bibsParam(doneSet);
        if (doneValue) {
            url.searchParams.set('done', doneValue);
        } else {
            url.searchParams.delete('done');
        }
        history.replaceState(null, '', unescapeCommas(url.pathname + url.search));
    }

    function refreshLinks() {
        var doneValue = bibsParam(doneSet);

        $('.js-done-carrier').each(function () {
            $(this).attr('href', withDone($(this).attr('href'), doneValue));
        });

        $('.js-done-input').val(doneValue);

        $('.js-toggle-done').each(function () {
            var $el = $(this);
            var bib = String($el.data('bib'));
            var candidate = new Set(doneSet);
            if (candidate.has(bib)) {
                candidate.delete(bib);
            } else {
                candidate.add(bib);
            }
            $el.attr('href', withDone($el.attr('href'), bibsParam(candidate)));
        });

        $('.js-remove-link').each(function () {
            var $el = $(this);
            var bib = String($el.data('bib'));
            var remaining = new Set(doneSet);
            remaining.delete(bib);
            $el.attr('href', withDone($el.attr('href'), bibsParam(remaining)));
        });
    }

    function applyRowState(bib, isDone) {
        $('.js-row[data-bib="' + bib + '"]')
            .toggleClass('has-text-grey-light', isDone)
            .toggleClass('done-bg', isDone);

        $('.js-toggle-done[data-bib="' + bib + '"]').each(function () {
            var $el = $(this);
            $el.toggleClass('has-text-success', isDone);
            $el.toggleClass('has-text-grey-light', !isDone);
            $el.find('i').toggleClass('fa-square-check', isDone).toggleClass('fa-square', !isDone);
        });

        $('.js-who-meta[data-bib="' + bib + '"]').toggleClass('has-text-grey', !isDone);
    }

    $(document).on('click', '.js-toggle-done', function (e) {
        e.preventDefault();
        var bib = String($(this).data('bib'));
        var isDone;
        if (doneSet.has(bib)) {
            doneSet.delete(bib);
            isDone = false;
        } else {
            doneSet.add(bib);
            isDone = true;
        }
        applyRowState(bib, isDone);
        updateUrlBar();
        refreshLinks();
    });

    refreshLinks();
});
