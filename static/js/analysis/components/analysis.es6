import $ from 'jquery';
import preact from 'preact';


class Spinner extends preact.Component {
    render() {
        return <div class="spinner">
            <div class="double-bounce1"></div>
            <div class="double-bounce2"></div>
        </div>
    }
}

class WordDetailHeader extends preact.Component {
    render({ active, enabled, code, label, onSelectPOS }) {
        const classNames = `tab ${enabled ? '' : 'empty'} ${active ? 'active' : ''}`;
        return <div onClick={() => enabled ? onSelectPOS(code) : null} class={classNames} >
            <span>{ label }</span>
        </div>
    }
}

class WordExplanations extends preact.Component {
    render({ info }) {
        return <div>
            { $.map(info, (entry) =>
                <div class="explanation">
                    { entry.definition }
                </div>
            ) }
        </div>
    }
}

class WordExamples extends preact.Component {
    render({ examples }) {
        return <div>
            { $.map(examples, (example) =>
                <div class="example">
                    { example.text }
                </div>
            ) }
        </div>
    }
}

class WordDetailBody extends preact.Component {
    render({ info, selection, onSelectPOS }) {
        const headers = [['noun', 'noun'],
                         ['verb', 'verb'],
                         ['adjective', 'adj'],
                         ['adverb', 'adv']]
        const selectedPOS = selection.POS ||
            $.grep(headers, (h) => info.info_by_pos[h[0]])[0][0]

        return <div>
            <header class="tab-group">
                { $.map(headers, (header) =>
                    <WordDetailHeader
                        active={selectedPOS === header[0]}
                        enabled={info.info_by_pos[header[0]]}
                        code={header[0]}
                        label={header[1]}
                        onSelectPOS={onSelectPOS} />
                )}
            </header>
            <section class="examples">
                <WordExamples examples={selection.word.sentences} />
            </section>
            <hr/>
            <section class="explanations">
                <WordExplanations info={info.info_by_pos[selectedPOS]} />
            </section>
        </div>
    }
}

class WordDetail extends preact.Component {
    render({ info, selection, onSelectPOS, onUnselectWord }) {
        if (selection.word) {
            return <div>
                <div class="card word-detail">
                    <header class="head">
                        <div class="arrow" onClick={() => onUnselectWord()}>&lt;</div>
                        <span class="label">{selection.word.word.token}</span>
                    </header>
                    <section class="body">
                        { !info
                            ? <Spinner />
                            : <WordDetailBody info={info}
                                            selection={selection}
                                            onSelectPOS={onSelectPOS} />
                        }
                    </section>
                </div>

                { info
                    ? <div class="attribution">
                        <div class="attribution_dictionary">
                            <a href={info.attribution_url}>{info.attribution_text}</a>
                        </div>
                        <div class="attribution_api">
                            <img src="/static/img/wordnik_badge.png"/>
                        </div>
                    </div>
                    : <div/>
                }
            </div>
        }
    }
}


class WordListItem extends preact.Component {
    render({ word, onSelectWord }) {
        return <div class="card word-item" onClick={() => onSelectWord(word)}>
            <div class="label">{ word.word.token }</div>
            <div class="arrow">&gt;</div>
        </div>
    }
}


class WordList extends preact.Component {
    render({ data, onSelectWord }) {
        return <div class="word-list">
            { $.map(data.words, item =>
                <WordListItem word={item} onSelectWord={onSelectWord} /> )}
        </div>
    }
}


class Analysis extends preact.Component {
    constructor() {
        super();
        this.state.selection = {};
        this.state.infoByToken = {};
    }

    handleSelectWord(word) {
        this.setState({ selection: { word } });

        $.getJSON({url: `/api/words/${word.word.token}`})
            .then((res) => {
                this.setState((prevState) => {
                    prevState.infoByToken[word.word.token]  = res
                });
            })
            .catch((err) => {
                console.error(err); // eslint-disable-line
                // TODO
            });
    }

    handleSelectPOS(POS) {
        this.setState((prevState) => {
            prevState.selection.POS = POS
        })
    }

    handleUnselectWord() {
        this.setState({ selection: { POS: undefined, word: undefined } });
    }

    render({ data }) {
        const selectedWord = this.state.selection.word
        return <div class={'analysis ' + (selectedWord ? 'detail' : 'list')}>
            <WordDetail
                selection={this.state.selection}
                info={selectedWord ? this.state.infoByToken[selectedWord.word.token] : undefined}
                onSelectPOS={(p) => this.handleSelectPOS(p)}
                onUnselectWord={() => this.handleUnselectWord()} />
            <WordList
                data={data}
                onSelectWord={(w) => this.handleSelectWord(w)} />
        </div>
    }
}


export { Analysis }
